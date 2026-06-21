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

## Phase 3: Scanners ✓ (11/12 done)

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