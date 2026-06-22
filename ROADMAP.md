# MigrateOS Development Roadmap

## Phase 1: Scaffolding ✓

- [x] Directory tree created
- [x] pyproject.toml, .gitignore, README stub, migrate_scan.py
- [x] All __init__.py files created
- [x] All .py stub files created
- [x] All .yml / .j2 template stubs created

## Phase 2: Utilities ✓

- [x] `src/utils/constants.py` — shared constants: blocklists, exclusions, secret patterns, runtime markers, install commands, stock SELinux modules, skip users, infra services, placeholder map, database services, task file names, J2 templates
- [x] `src/utils/paths.py` — is_blocked_path, is_excluded_file, is_secret_file, detect_secrets_in_file, detect_runtime, suggest_install, detect_includes
- [x] `src/utils/command.py` — safe_run (never raises), force_run (raises on failure)
- [x] `src/utils/yaml_utils.py` — load_yaml, save_yaml
- [x] `src/utils/dnf_utils.py` — detect_dnf_version (DNF4 vs DNF5), return_userinstalled_cmd, return_group_list_cmd, return_extras_cmd

## Phase 3: Scanners ✓ (11/11 done)

- [x] `src/scanner/os_facts.py`
- [x] `src/scanner/packages.py`
- [x] `src/scanner/services.py`
- [x] `src/scanner/users.py`
- [x] `src/scanner/directories.py`
- [x] `src/scanner/configs.py`
- [x] `src/scanner/cron.py`
- [x] `src/scanner/selinux.py`
- [x] `src/scanner/network.py`
- [x] `src/scanner/sysctl.py`
- [x] `src/scanner/containers.py`

## Phase 4: Bundler ✓

- [x] `src/bundler/file_collector.py` — 9 functions: copy_file_from_disk, write_file_from_content, bundle_config_files, bundle_custom_repos, bundle_cron_files, bundle_sysctl_files, bundle_services, bundle_network_files, bundle_manifest

## Phase 5: Generator ✓

- [x] `src/generator/ansible_generator.py` — 9 functions: apply_substitutions, render_j2, detect_databases, extract_repo_filenames, prefix_group_names, build_template_vars, copy_task_files, copy_bundled_files, generate
- [x] 7 Jinja2 templates (.j2): ansible.cfg, requirements.yml, inventory.ini, site.yml, WARNINGS.md, group_vars/new_server.yml, group_vars/vault.example.yml
- [x] 13 task YAML files + handlers: main.yml, bootstrap, validate, repos, packages, users, directories, configs, cron, sysctl, services, selinux, verification, handlers/main.yml

## Phase 6: CLI ✓

- [x] `src/cli/cli.py` — 3 subcommands (scan, generate, scan-and-generate), manifest assembly, bundler integration, summary output
- [x] `migrate_scan.py` — entry point

## Tests (193 tests across 19 files) ✓

- [x] `tests/utils/` — test_command (7), test_dnf_utils (6), test_paths (32), test_yaml_utils (6)
- [x] `tests/scanner/` — 11 files, 70 tests
- [x] `tests/bundler/` — test_file_collector (16)
- [x] `tests/generator/` — test_ansible_output (23)
- [x] `tests/cli/` — test_cli (33)

## Phase 8: Polish ✓

- [x] `README.md` — full documentation with architecture
- [x] `examples/example_manifest.yml` — complete realistic manifest
- [x] `examples/generated-ansible/` — generated example output
- [x] `ROADMAP.md` — this file, updated
- [x] Stale docstring cleanup (yaml_utils.py, file_collector.py, ansible_generator.py, selinux.py)

## CI/CD ✓

- [x] `.github/workflows/test_code.yml` — pytest on push, ubuntu-latest, Python 3.13

---

## Planned Features — HIGH Priority

- [ ] Full system scan mode — `--full-scan` flag that walks `/etc/`, `/opt/`, `/srv/`, `/home/` automatically instead of requiring `--config-path` / `--app-path`. Applies stock config filtering to reduce noise.
- [ ] Package version pinning — store exact RPM version+release in manifest, not just package name. Ensure target installs identical versions.
- [ ] Config diffing (stock vs custom) — diff source configs against stock Fedora package defaults. Flag modified files, skip unmodified ones. Reduces manifest noise significantly.
- [ ] Progress bars — real-time progress feedback during scan and generate phases. Show which scanner is running, how many packages/services/configs found, bundler copy progress. Use `rich` or simple counter-based output.
- [ ] Firewalld scanner — `src/scanner/firewalld.py`. Parse zones, services, ports, rich rules, direct rules, ipsets, policies, custom XMLs. Generate `firewalld.yml` task template. Add to `TASK_FILE_NAMES` and `main.yml` imports.

## Planned Features — MEDIUM Priority

- [ ] Database dump integration — `--dump-databases` flag that runs `pg_dump`, `mysqldump`, `redis-cli BGSAVE`, `mongodump` automatically. Includes dumps in output for manual restore on target.
- [ ] Container migration — `--commit-containers` flag that runs `docker commit` + `docker save` for each running container. Produces tarballs loadable on the target.
- [ ] Target server validation — post-migration verification playbook. Check package versions, service states, config file checksums, sysctl values. Produce a diff report.
- [ ] Boot configuration — scan `/etc/default/grub`, `/etc/dracut.conf.d/`, kernel command line. Detect custom boot parameters.
- [ ] Network filesystems — detect NFS, CIFS/SMB mounts in `/etc/fstab`. Detect autofs configuration, iSCSI targets. Warn in manifest.
- [ ] Logrotate configuration — scan `/etc/logrotate.conf` and `/etc/logrotate.d/`. Capture custom rotation rules for app logs.
- [ ] User home directory content — optionally capture `.bashrc`, `.bash_profile`, `.vimrc`, `.gitconfig`, `~/.config/` app configs, user crontabs (`crontab -l`). Controlled by `--include-home-configs` flag.
- [ ] Time synchronization — scan `/etc/chrony.conf` or `/etc/ntp.conf`. Capture NTP server settings.

## Planned Features — LOW Priority

- [ ] Pre/post migration hooks — run custom scripts before and after migration. Define in manifest under `hooks.pre_migration` and `hooks.post_migration`.
- [ ] Multi-server migration — scan multiple servers in one run, produce one Ansible project with multiple plays. Handle inter-server dependencies.
- [ ] Incremental migration — detect what changed since last scan, only update changed parts in manifest, only regenerate affected Ansible tasks.
- [ ] Rollback capability — generate an undo playbook that reverts config files (using Ansible's `backup: yes` backups), stops started services, reverts sysctl changes.
- [ ] Secret rotation — generate new random passwords/API keys during migration. Store in ansible-vault. Integrate with certbot for TLS certificate renewal.
- [ ] Hardware-specific detection — GPU drivers (NVIDIA/AMD), firmware files, device-specific udev rules. Warn about hardware-dependent configs.
- [ ] LVM/disk layout — scan physical volumes, volume groups, logical volumes. Capture filesystem types, mount options, partitioning. Warn about hardware-dependent layout.
- [ ] RAID configuration — scan `/etc/mdadm.conf`. Capture RAID level, devices, spare drives.
- [ ] Encryption — detect LUKS/dm-crypt configuration. Warn about encryption keys (never copy keys).
- [ ] Mail configuration — scan `/etc/postfix/main.cf`, `/etc/aliases`. Capture mail routing settings.
- [ ] Proxy configuration — scan `/etc/environment`, `/etc/profile.d/` for proxy settings. Capture DNF proxy, Docker proxy configs.
- [ ] Auditing — scan `/etc/audit/` rules. Capture auditd configuration.
- [ ] Compliance — CIS benchmark compliance status, STIG compliance, security hardening configs.
- [ ] Tmpfiles configuration — scan `/etc/tmpfiles.d/`. Capture temporary file creation rules.
- [ ] Udev rules — scan `/etc/udev/rules.d/`. Capture custom device rules.
- [ ] Polkit rules — scan `/etc/polkit-1/rules.d/`. Capture privilege escalation rules.
- [ ] D-Bus configuration — scan `/etc/dbus-1/`. Capture bus policies.

## Firewalld (Deferred)

- [ ] `src/scanner/firewalld.py`
- [ ] `tests/scanner/test_firewalld.py`
- [ ] `firewalld.yml` task template
- [ ] Firewalld variables in `build_template_vars()` and `new_server.yml.j2`
- [ ] Import in `main.yml` and `TASK_FILE_NAMES`
