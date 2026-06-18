"""Scan systemd services: enabled state, running state, custom units,
activation type, tier classification."""

from pathlib import Path
from typing import List
from src.utils.command import safe_run
from src.utils.paths import is_blocked_path
from src.utils.constants import INFRASTRUCTURE_SERVICES


def parse_unit_files(text: str) -> dict:
    """Parse systemctl list-unit-files output → {name: state}."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            result[parts[0]] = parts[1]
    return result

def parse_running_units(text: str) -> set:
    """Parse systemctl list-units output → set of running service names."""
    result = set()
    for line in text.splitlines():
        parts = line.split()
        if parts:
            result.add(parts[0])
    return result


def scan_custom_units(systemd_base: Path = Path("/etc/systemd/system")) -> List[dict]:
    """Scan *.service files. Skip symlinks to /usr/lib/ (stock units)."""
    custom = []
    if systemd_base.is_dir():
        for svc_file in sorted(systemd_base.glob("*.service")):
            if svc_file.is_symlink() and "/usr/lib/" in str(svc_file.resolve()):
                continue
            if is_blocked_path(svc_file):
                continue
            custom.append({
                "name": svc_file.stem,
                "unit_file": svc_file.read_text(encoding="utf-8", errors="ignore"),
                "path": str(svc_file),
            })
    return custom

def parse_environment_file(unit_path: Path) -> List[str]:
    """Extract EnvironmentFile= and EnvironmentFile=- directives from unit file."""
    try:
        content = unit_path.read_text(encoding="utf-8", errors="ignore")
    except (PermissionError, OSError):
        return []
    env_files = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("EnvironmentFile="):
            value = line.split("=", 1)[1]
            if value.startswith("-"):
                value = value[1:]
            env_files.append(value)
    return env_files


def detect_timer_activation(name: str, systemd_base: Path = Path("/etc/systemd/system")) -> bool:
    """Check if <name>.timer exists alongside the service."""
    return (systemd_base / f"{name}.timer").is_file()


def detect_socket_activation(name: str, systemd_base: Path = Path("/etc/systemd/system")) -> bool:
    """Check if <name>.socket exists alongside the service."""
    return (systemd_base / f"{name}.socket").is_file()

def classify_service(name: str) -> str:
    """Return "infrastructure" for known infra services, "application" otherwise."""
    base = name.replace(".service", "").replace("@", "")
    if base in INFRASTRUCTURE_SERVICES:
        return "infrastructure"
    return "application"

def collect() -> dict:
    _, unit_files_out, _ = safe_run(
        ["systemctl", "list-unit-files", "--type=service", "--no-legend", "--no-pager"]
    )
    _, running_out, _ = safe_run(
        ["systemctl", "list-units", "--type=service", "--state=running",
         "--no-legend", "--no-pager"]
    )

    units = parse_unit_files(unit_files_out)
    running = parse_running_units(running_out)
    custom_units = scan_custom_units()

    services = []
    for name, state in sorted(units.items()):
        base_name = name.replace(".service", "")
        is_custom = any(c["name"] == base_name for c in custom_units)
        unit_data = None
        env_files = []

        if is_custom:
            unit_path = Path("/etc/systemd/system", name)
            if not unit_path.exists():
                unit_path = Path("/etc/systemd/system", base_name + ".service")
            if unit_path.is_file():
                unit_data = unit_path.read_text(encoding="utf-8", errors="ignore")
                env_files = parse_environment_file(unit_path)

        services.append({
            "name": name,
            "enabled": state == "enabled",
            "state": "running" if name in running else "inactive",
            "custom_unit": unit_data is not None,
            "unit_file": unit_data,
            "environment_files": env_files,
            "timer_activated": detect_timer_activation(base_name),
            "socket_activated": detect_socket_activation(base_name),
            "service_tier": classify_service(name),
        })

    return {"services": services}
