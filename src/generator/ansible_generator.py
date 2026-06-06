"""Generate a complete Ansible project from a manifest YAML file.

TODO:
    - Implement _build_template_vars(manifest: dict, output_dir: Path) -> dict
      (transform manifest into flat template variable dict: service tier splits, computed booleans, etc.)
    - Implement _render_j2(env, template_name, dest, tv) -> None (render a single Jinja2 template)
    - Implement _apply_substitutions(content: str, tv: dict) -> str (replace __PLACEHOLDER__ strings)
    - Implement _copy_task_files(tv: dict) -> None (copy all 14 task YAML files with placeholder substitution)
    - Implement _copy_bundled_files(manifest: dict, output_dir: Path) -> None (copy files/ to Ansible role)
    - Implement generate(manifest_path: Path, output_dir: Path) -> None (main orchestrator)
    - Template variables to compute:
      - services_infra / services_app (split by service_tier)
      - config_files (copy_method != "directory") / config_dirs (copy_method == "directory")
      - custom_repo_files (strip .repo suffix)
      - dnf_groups (prefix with @)
      - Computed booleans: has_firewalld, has_cron, has_sysctl, has_containers, has_databases
    - List of task files (order matters): bootstrap, validate, repos, packages, users, directories, configs, cron, sysctl, services, firewalld, selinux, verification
"""
