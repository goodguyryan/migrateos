# MigrateOS Development Roadmap

## Phase 1: Scaffolding ✓ (current)

- [x] Directory tree created
- [x] pyproject.toml written
- [x] .gitignore written
- [x] All __init__.py files created
- [x] All .py stub files created
- [x] All .yml / .j2 template stubs created

## Phase 2: Utilities (4 files)

- [ ] src/utils/paths.py — blocklist, exclusions, secret detection, runtime detection, include scanning
- [ ] src/utils/command.py — run(), run_ok(), run_output()
- [ ] src/utils/yaml_utils.py — load_yaml(), save_yaml()
- [ ] src/utils/dnf_version.py — detect_dnf_cmd(), userinstalled_cmd(), group_list_cmd()

## Phase 3: Scanners (12 files)

- [ ] src/scanner/os_facts.py
- [ ] src/scanner/packages.py
- [ ] src/scanner/services.py
- [ ] src/scanner/users.py
- [ ] src/scanner/directories.py
- [ ] src/scanner/configs.py
- [ ] src/scanner/firewalld.py
- [ ] src/scanner/cron.py
- [ ] src/scanner/selinux.py
- [ ] src/scanner/network.py
- [ ] src/scanner/sysctl.py
- [ ] src/scanner/containers.py

## Phase 4: Bundler (1 file)

- [ ] src/bundler/file_collector.py

## Phase 5: Generator (templates + code)

**Jinja2 templates (.j2):**
- [ ] src/generator/templates/ansible.cfg.j2
- [ ] src/generator/templates/requirements.yml.j2
- [ ] src/generator/templates/inventory.ini.j2
- [ ] src/generator/templates/site.yml.j2
- [ ] src/generator/templates/group_vars/new_server.yml.j2
- [ ] src/generator/templates/group_vars/vault.example.yml.j2
- [ ] src/generator/templates/WARNINGS.md.j2

**Task YAML files (plain YAML, no .j2):**
- [ ] src/generator/templates/roles/migrated_server/tasks/main.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/bootstrap.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/validate.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/repos.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/packages.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/users.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/directories.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/configs.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/cron.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/sysctl.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/services.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/firewalld.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/selinux.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/verification.yml
- [ ] src/generator/templates/roles/migrated_server/tasks/handlers/main.yml

**Generator code:**
- [ ] src/generator/ansible_generator.py

## Phase 6: CLI (2 files)

- [ ] src/cli.py
- [ ] migrate_scan.py (updated)

## Phase 7: Tests (9 files)

- [ ] tests/conftest.py
- [ ] tests/test_dnf_parsing.py
- [ ] tests/test_systemctl_parsing.py
- [ ] tests/test_secret_detection.py
- [ ] tests/test_runtime_detection.py
- [ ] tests/test_firewalld_parsing.py
- [ ] tests/test_config_include_scanning.py
- [ ] tests/test_manifest_roundtrip.py
- [ ] tests/test_ansible_output.py

## Phase 8: Polish (3 items)

- [ ] README.md
- [ ] examples/example_manifest.yml
- [ ] examples/generated-ansible/ (run tool to produce)

