# MigrateOS

Scan a Fedora server and generate an idempotent Ansible project to recreate it.

## What It Does

MigrateOS inspects a running Fedora server — its installed packages, systemd services,
users, config files, cron jobs, SELinux policy, sysctl parameters, network connections,
and container runtimes — and produces two things:

1. A **YAML manifest** (`manifest.yml`) that a human reviews and can edit
2. A complete, runnable **Ansible project** that re-creates the server setup on a new
   Fedora target using idempotent playbooks

The output is designed to be safe: secrets are never copied, system files are
blocklisted, and anything that requires manual intervention (databases, containers,
SELinux modules) produces explicit warnings with step-by-step instructions.

## What It Does NOT Do

- Copy secrets (passwords, keys, tokens, credentials)
- Copy system identity files (`/etc/machine-id`, `/etc/hostname`, `/etc/fstab`,
  `/etc/shadow`, SSH host keys)
- Preserve UIDs or GIDs (Ansible auto-assigns them on the target)
- Copy application code (runtime detection and install suggestions only)
- Migrate databases, containers, or network config automatically
- Clone `/proc/`, `/sys/`, `/dev/`, `/tmp/`, `/run/`, or `/var/log/` contents
- Configure firewalld (planned, not yet implemented)

## Architecture

```
                     Source Fedora Server
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌────────────┐   ┌────────────┐    ┌──────────────┐
   │ os_facts   │   │ packages   │    │  services    │  ... 11 scanners
   │ .collect() │   │ .collect() │    │  .collect()  │
   └─────┬──────┘   └─────┬──────┘    └──────┬───────┘
         │                │                  │
         └────────────────┼──────────────────┘
                          ▼
                   ┌─────────────┐
                   │  manifest   │  ← YAML, human reviews and edits
                   │     .yml    │
                   └──────┬──────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       ┌────────────┐         ┌──────────────┐
       │  Bundler   │         │  Generator   │
       │ copies     │         │ renders      │
       │ files with │         │ Jinja2 .j2   │
       │ safety     │         │ + task YAML  │
       │ checks     │         │ with place-  │
       └─────┬──────┘         │ holders      │
             │                └──────┬───────┘
             └───────────┬───────────┘
                         ▼
                 ┌──────────────┐
                 │  Ansible     │
                 │  Project     │
                 │  (output/)   │
                 └──────────────┘
```

### Layers

#### 1. Utilities (`src/utils/`)

Shared infrastructure used by every other layer.

| Module | Purpose |
|--------|---------|
| `constants.py` | All shared data: blocklists, exclusion patterns, secret detection regex, runtime markers, install commands, stock SELinux modules, skip-user list, infrastructure service names |
| `command.py` | `safe_run()` returns `(bool, stdout, stderr)` and never raises. `force_run()` returns stdout and raises on failure. Both enforce `shell=False`. |
| `dnf_utils.py` | Abstracts DNF4 vs DNF5 CLI differences. `detect_dnf_version()` queries the system, `return_*_cmd()` helpers build version-appropriate command lists. |
| `paths.py` | Safety core: `is_blocked_path()`, `is_excluded_file()`, two-tier secret detection (`is_secret_file()` + `detect_secrets_in_file()`), `detect_runtime()`, `suggest_install()`, `detect_includes()`. |
| `yaml_utils.py` | `load_yaml()` returns `{}` on missing files. `save_yaml()` creates parent dirs, uses block style and sorted keys. |

#### 2. Scanners (`src/scanner/`)

Each scanner inspects one aspect of the source server. All follow the same pattern:
parser functions accept an optional `text` parameter (injectable for testing);
a `collect()` orchestrator runs real commands and returns a structured dict.

| Scanner | What it scans | Source |
|---------|--------------|--------|
| `os_facts.py` | OS identity, kernel, hostname, timezone, locale, SELinux | `/etc/os-release`, `uname`, `hostnamectl`, `timedatectl`, `localectl`, `getenforce` |
| `packages.py` | Installed packages, DNF groups, extras, custom repos | `dnf repoquery`, `dnf group list`, `dnf list --extras`, `/etc/yum.repos.d/` |
| `services.py` | systemd services: enabled state, running state, custom units, activation type, infrastructure vs application tier | `systemctl list-unit-files`, `systemctl list-units`, `/etc/systemd/system/` |
| `users.py` | Local users (UID >= 1000) and groups, optional SSH keys and sudoers | `/etc/passwd`, `/etc/group`, `~/.ssh/authorized_keys`, `/etc/sudoers.d/` |
| `directories.py` | App directory metadata: ownership, mode, runtime detection, install suggestions | Filesystem stat + runtime marker files |
| `configs.py` | Config files and directories with SHA-256, preview, secret/include detection, copy method decision | Filesystem walk with safety filters |
| `cron.py` | Cron scripts and systemd timers | `/etc/cron.*`, `/etc/systemd/system/*.timer` |
| `selinux.py` | SELinux mode and custom policy modules | `getenforce`, `sestatus`, `semodule -l` |
| `network.py` | NetworkManager connections (detection by default, optional copy) | `nmcli -t connection show` |
| `sysctl.py` | Kernel parameters | `/etc/sysctl.conf`, `/etc/sysctl.d/*.conf` |
| `containers.py` | Docker and Podman containers (detection only) | `docker ps`, `podman ps` |

#### 3. Bundler (`src/bundler/`)

One module: `file_collector.py`. Copies files from the source server into the output
directory with full safety re-verification. Uses two primitives:

- **`copy_file_from_disk()`** — copies from filesystem with safety chain: blocked → excluded → secret filename → secret content → `shutil.copy2`
- **`write_file_from_content()`** — writes content already in the manifest (pre-verified by the scanner)

Section collectors iterate their manifest section and call the appropriate primitive.
`bundle_manifest()` orchestrates all sections and returns `{copied, skipped, warnings}`.

Output structure:
```
output_dir/
├── files/          (consumed by generator → Ansible role files/)
│   ├── etc/nginx/nginx.conf
│   ├── etc/yum.repos.d/custom.repo
│   ├── cron.d/backup.sh
│   ├── sysctl.d/99-custom.conf
│   └── systemd/myapp.service
└── review/         (human inspects, NOT in Ansible)
    └── NetworkManager/*.nmconnection
```

#### 4. Generator (`src/generator/`)

One code module (`ansible_generator.py`) + 21 template files. Entry point: `generate(manifest_path, output_dir)`.

**Two-template system** — this is the critical design decision:

| Template type | Files | Engine | Why |
|--------------|-------|--------|-----|
| `.j2` (Jinja2) | 7 files (group_vars, WARNINGS, ansible.cfg, inventory, site.yml, requirements, vault) | Jinja2 with `FileSystemLoader` | Needs loops over packages, services, users; conditional sections for warnings |
| `.yml` (task files) | 13 task files + handlers/main.yml | `str.replace()` for `__PLACEHOLDER__` only | File contains Ansible `{{ }}` syntax which would crash Jinja2 |

The bridge between them is `build_template_vars()`, which transforms the nested manifest
dict into a flat dictionary of ~40 keys: service tier splits, config file/dir splits,
computed booleans (`has_cron`, `has_sysctl`, `has_containers`, `has_databases`, etc.),
and metadata.

#### 5. CLI (`src/cli/`)

Three subcommands via `argparse`:

| Command | What it does |
|---------|-------------|
| `scan` | Runs all 11 scanners, assembles the manifest, calls the bundler, saves `manifest.yml`, prints summary |
| `generate` | Loads manifest YAML, calls `ansible_generator.generate()` |
| `scan-and-generate` | Runs `scan` then `generate` in sequence |

Flags: `--output`, `--config-path` (multiple), `--app-path` (multiple),
`--include-network`, `--include-ssh-keys`, `--include-sudoers`, `--dry-run`.

### Data Flow

1. **Scan phase:** Each scanner's `collect()` returns a dict. The CLI assembles them into a manifest dict with keys matching scanner names. Special handling: `configs` returns a 3-tuple repacked into `{config_files, secrets_required, warnings}`; `directories` returns a bare list.
2. **Bundler phase:** `bundle_manifest()` iterates the manifest's config/packages/cron/sysctl/services/network sections and copies files to `output_dir/files/` and optionally `output_dir/review/`.
3. **Generate phase:** `generate()` loads the manifest YAML, calls `build_template_vars()` to flatten it, renders 7 Jinja2 templates, copies 13 task YAML files with placeholder substitution, and copies bundled files into the Ansible role.

## Quick Start

### Prerequisites

- Python 3.9+
- Run the scan on a Fedora source server (uses DNF, systemctl, firewalld-cmd, nmcli)
- Generate and run the Ansible output on any machine with Ansible installed

### Install

```bash
git clone https://github.com/yourorg/migrateos.git
cd migrateos
pip install -e .
```

### Scan a Server

```bash
python migrate_scan.py scan \
    --output ./migration-output \
    --config-path /etc/nginx \
    --config-path /etc/ssh/sshd_config.d \
    --app-path /opt/myapp
```

### Review the Manifest

```bash
cat migration-output/manifest.yml
```

### Generate Ansible

```bash
python migrate_scan.py generate \
    --manifest migration-output/manifest.yml \
    --output migration-output
```

Or do it all at once:

```bash
python migrate_scan.py scan-and-generate \
    --output ./migration-output \
    --config-path /etc/nginx \
    --app-path /opt/myapp
```

### Run on Target Server

```bash
cd migration-output/generated-ansible

# Install required Ansible collection
ansible-galaxy collection install -r requirements.yml

# Edit inventory.ini — replace CHANGE_ME with new server IP
vim inventory.ini

# Dry run (safe, no changes)
ansible-playbook site.yml --check --diff

# Apply
ansible-playbook site.yml
```

### Review Warnings

Open `generated-ansible/WARNINGS.md` for a human-readable checklist of:

- Secrets that were found and NOT copied
- Database services that need manual dump/restore
- Containers that need manual commit/push
- Network config that needs manual review
- Custom SELinux modules that cannot be auto-migrated
- Next steps checklist

## How Secrets Are Handled

### Tier 1: Filename Detection

Files matching these patterns are **never copied**:

- Names containing: `.env`, `key`, `secret`, `token`, `credential`, `private`,
  `id_rsa`, `id_ed25519`, `id_ecdsa`, `tls.key`, `server.key`
- Extensions: `.pem`, `.key`
- Exception: `id_rsa.pub` (public key, safe to copy)

### Tier 2: Content Scanning

Files are scanned with a regex for patterns like `PASSWORD=`, `SECRET=`, `API_KEY=`,
`DATABASE_URL=`, `JWT_SECRET=`, etc. Files containing matches are still copied but
flagged in `WARNINGS.md` so the human can verify and handle them.

### Blocked Paths

These paths are **never copied under any circumstances**:

| Type | Paths |
|------|-------|
| Exact | `/etc/machine-id`, `/etc/hostname`, `/etc/hosts`, `/etc/fstab`, `/etc/shadow`, `/etc/gshadow`, `/etc/passwd`, `/etc/group`, `/etc/crypttab`, `/etc/resolv.conf` |
| Prefix | `/etc/ssh/ssh_host_*`, `/var/log/`, `/tmp/`, `/run/`, `/proc/`, `/sys/`, `/dev/` |

## Database Migration (Manual)

Database services (PostgreSQL, MariaDB/MySQL, Redis, MongoDB) are detected and listed
in `WARNINGS.md`. Database state cannot be auto-migrated. You must:

**PostgreSQL:**
```bash
pg_dump -U postgres dbname > dbname.sql
# On target: psql -U postgres dbname < dbname.sql
```

**MySQL / MariaDB:**
```bash
mysqldump -u root -p dbname > dbname.sql
# On target: mysql -u root -p dbname < dbname.sql
```

**Redis:**
```bash
redis-cli BGSAVE
# Copy dump.rdb from source data directory to target
```

**MongoDB:**
```bash
mongodump --db dbname --out /backup/
# On target: mongorestore /backup/
```

## Container Migration (Manual)

Running Docker and Podman containers are detected but not auto-migrated. You must:

```bash
# Commit each container to an image
docker commit mycontainer mycontainer:latest
# or: podman commit mycontainer mycontainer:latest

# Push to a registry
docker push myregistry/mycontainer:latest
# or: podman push myregistry/mycontainer:latest

# On target: pull and run
docker run -d myregistry/mycontainer:latest
```

## Network Configuration

NetworkManager connections are detected (`--include-network` flag). When enabled,
connection files are copied to the `review/` directory for human inspection — they
are never automatically applied to the target server because network config is
server-specific (different interfaces, IPs, subnets).

## SELinux

Custom (non-stock) SELinux policy modules are detected and warned about. They cannot
be auto-migrated because SELinux modules are compiled against the running kernel and
policy version. You must recompile and install custom modules on the target server.

## Safety Limitations

- **Fedora only.** The tool uses DNF, systemctl, firewalld-cmd, and nmcli — these
  are Fedora/RHEL-specific. It will not work on Debian, Ubuntu, Arch, or Alpine.
- **UIDs and GIDs are not preserved.** Ansible auto-assigns numeric IDs on the target
  to avoid collisions. If your application depends on specific numeric IDs, adjust
  `group_vars/new_server.yml` before running the playbook.
- **Firewalld not yet scanned.** Firewall configuration is not collected. The target
  server gets no firewalld rules. This is planned for a future release.
- **Symlinks are followed.** The resolved target file is copied, not the symlink
  itself. Warnings are emitted in the manifest.
- **App directories are metadata-only.** The `--app-path` flag detects runtimes
  and suggests install commands. Application code is not copied.
- **No rollback.** The generated Ansible is idempotent (safe to re-run) but there
  is no "undo" playbook. Always run with `--check --diff` first.

## License

MIT
