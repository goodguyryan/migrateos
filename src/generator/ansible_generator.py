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
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import shutil
from src.utils.yaml_utils import load_yaml
from src.utils.constants import (PLACEHOLDER_MAP, 
                                 DATABASE_SERVICES,
                                 TASK_FILE_NAMES,
                                 HANDLER_FILE,
								 J2_TEMPLATES)

def apply_substitutions(content: str, template_variables: dict) -> str:
	for placeholder, key in PLACEHOLDER_MAP.items():
		if placeholder in content and key in template_variables:
			content = content.replace(placeholder, template_variables[key])
	
	return content

def render_j2(j2_env: Environment, template_name: str, dest: Path, template_variables: dict) -> None:
    template = j2_env.get_template(template_name)
    rendered_content = template.render(**template_variables)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered_content, encoding="utf-8")

def detect_databases(services: list) -> bool:
	for service in services:
		base = service["name"].replace(".service", "").replace("@", "")
		if base in DATABASE_SERVICES:
			return True
	
	return False

def extract_repo_filenames(custom_repos: list) -> list:
    return [repo["filename"].replace(".repo", "") for repo in custom_repos]

def prefix_group_names(groups: list) -> list:
    return [f"@{group}" for group in groups]

def build_template_vars(manifest: dict) -> dict:
    os_facts = manifest.get("os_facts", {})
    source_os = os_facts.get("os", "")
    source_version = os_facts.get("version", "")
    source_hostname = os_facts.get("hostname", "")
    source_kernel = os_facts.get("kernel", "")
    source_architecture = os_facts.get("architecture", "")
    source_timezone = os_facts.get("timezone", "")
    source_locale = os_facts.get("locale", "")

    selinux_facts = os_facts.get("selinux", {})
    selinux_status = selinux_facts.get("status", "enabled")
    selinux_mode = selinux_facts.get("mode", "enforcing")

    packages_section = manifest.get("packages", {})
    dnf_packages = packages_section.get("packages", [])
    dnf_groups = prefix_group_names(packages_section.get("groups", []))
    dnf_extras = packages_section.get("extras", [])
    custom_repo_files = extract_repo_filenames(packages_section.get("custom_repos", []))

    services = manifest.get("services", {}).get("services", [])
    services_infra = [s for s in services if s.get("service_tier") == "infrastructure"]
    services_app = [s for s in services if s.get("service_tier") == "application"]

    users_section = manifest.get("users", {})
    migrated_users = users_section.get("users", [])
    migrated_groups = users_section.get("groups", [])

    app_directories = manifest.get("directories", [])

    configs_section = manifest.get("configs", {})
    config_files = []
    config_dirs = []
    for entry in configs_section.get("config_files", []):
        if entry.get("copy_method") == "directory":
            config_dirs.append(entry)
        else:
            config_files.append(entry)
    config_warnings = configs_section.get("warnings", [])
    secrets_required = configs_section.get("secrets_required", [])

    cron_section = manifest.get("cron", {})
    cron_files = cron_section.get("files", [])
    cron_timers = cron_section.get("timers", [])

    sysctl_files = manifest.get("sysctl", {}).get("files", [])

    network_section = manifest.get("network", {})
    network_connections = network_section.get("connections", [])
    network_warning = network_section.get("warning")

    containers_section = manifest.get("containers", {})
    container_runtimes = containers_section.get("runtimes", [])
    running_containers = containers_section.get("running_containers", [])
    container_warning = containers_section.get("warning")

    selinux_section = manifest.get("selinux", {})
    custom_selinux_modules = selinux_section.get("custom_modules", [])
    selinux_warning = selinux_section.get("warning")


    has_cron = bool(cron_files or cron_timers)
    has_sysctl = bool(sysctl_files)
    has_containers = bool(running_containers)
    has_custom_repos = bool(custom_repo_files)
    has_custom_units = any(s.get("custom_unit") for s in services)
    has_secrets = bool(secrets_required)
    has_databases = detect_databases(services)
    has_network = bool(network_connections) and not network_warning
    has_custom_selinux = bool(custom_selinux_modules)

    version_note = f"Generated by MigrateOS v0.1.0 from {source_hostname}"
    timestamp = datetime.now().isoformat()

    return {
        # OS facts
        "source_os": source_os,
        "source_version": source_version,
        "source_hostname": source_hostname,
        "source_kernel": source_kernel,
        "source_architecture": source_architecture,
        "source_timezone": source_timezone,
        "source_locale": source_locale,
        "selinux_status": selinux_status,
        "selinux_mode": selinux_mode,

        "dnf_packages": dnf_packages,
        "dnf_groups": dnf_groups,
        "dnf_extras": dnf_extras,
        "custom_repo_files": custom_repo_files,

        "services_infra": services_infra,
        "services_app": services_app,

        "migrated_users": migrated_users,
        "migrated_groups": migrated_groups,

        "app_directories": app_directories,

        "config_files": config_files,
        "config_dirs": config_dirs,
        "config_warnings": config_warnings,
        "secrets_required": secrets_required,

        "cron_files": cron_files,
        "cron_timers": cron_timers,

        "sysctl_files": sysctl_files,

        "network_connections": network_connections,
        "network_warning": network_warning,

        "container_runtimes": container_runtimes,
        "running_containers": running_containers,
        "container_warning": container_warning,

        "custom_selinux_modules": custom_selinux_modules,
        "selinux_warning": selinux_warning,

        "has_cron": has_cron,
        "has_sysctl": has_sysctl,
        "has_containers": has_containers,
        "has_custom_repos": has_custom_repos,
        "has_custom_units": has_custom_units,
        "has_secrets": has_secrets,
        "has_databases": has_databases,
        "has_network": has_network,
        "has_custom_selinux": has_custom_selinux,

        "version_note": version_note,
        "timestamp": timestamp,
    }

def copy_task_files(template_variables: dict, template_dir: Path, tasks_dest: Path) -> None:
	tasks_dest.mkdir(parents=True, exist_ok=True)
      
	for file_name in TASK_FILE_NAMES:
		src = template_dir / file_name
		dest = tasks_dest / file_name
		content = src.read_text(encoding="utf-8")
		content = apply_substitutions(content, template_variables)
		dest.write_text(content, encoding="utf-8")
	
	handler_src = template_dir / HANDLER_FILE
	if handler_src.exists():
		handler_content = handler_src.read_text(encoding="utf-8")
		handler_content = apply_substitutions(handler_content, template_variables)
		handler_dest = tasks_dest / HANDLER_FILE
		handler_dest.parent.mkdir(parents=True, exist_ok=True)
		handler_dest.write_text(handler_content, encoding="utf-8")

def copy_bundled_files(output_dir: Path, ansible_dir: Path) -> None:
	src = output_dir / "files"
	if not src.is_dir():
		return
	
	dest = ansible_dir / "roles" / "migrated_server" / "files"
	shutil.copytree(src, dest, dirs_exist_ok=True)

def generate(manifest_path: Path, output_dir: Path) -> None:
	manifest = load_yaml(manifest_path)

	ansible_dir = output_dir / "generated-ansible"
	tasks_dir = ansible_dir / "roles" / "migrated_server" / "tasks"
	group_vars_dir = ansible_dir / "group_vars"

	for directory in [ansible_dir, tasks_dir, group_vars_dir]:
		directory.mkdir(parents=True, exist_ok=True)
	
	template_vars = build_template_vars(manifest)

	template_dir = Path(__file__).parent.joinpath("templates")
	j2_env = Environment(loader=FileSystemLoader(str(template_dir)))

	for template_name, output_name in J2_TEMPLATES.items():
		dest = ansible_dir / output_name
		render_j2(j2_env, template_name, dest, template_vars)

	copy_task_files(template_vars, template_dir / "roles" / "migrated_server" / "tasks", tasks_dir)

	copy_bundled_files(output_dir, ansible_dir)
