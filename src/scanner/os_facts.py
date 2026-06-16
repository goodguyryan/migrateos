"""Collect OS identity: distribution, kernel, hostname, timezone, locale, SELinux status."""

from pathlib import Path
from src.utils.command import safe_run

def parse_os_release(text: str = None) -> dict:
    if text is None:
        text = Path("/etc/os-release").read_text(encoding="utf-8", errors="ignore")
    
    data = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    
    return data

def parse_timezone(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Timezone="):
            return line.split("=", 1)[1]
    return ""

def parse_locale(text: str) -> str:
    for line in text.splitlines():
        if "LANG=" in line:
            _, _, after = line.partition("LANG=")
            return after.split()[0] if after else ""
    return ""

def collect() -> dict:
    os_info = parse_os_release()
    _, kernel, _ = safe_run(["uname", "-r"])
    _, architecture, _ = safe_run(["uname", "-m"])
    _, hostname, _ = safe_run(["hostnamectl", "--static"])
    _, timedatectl_output, _ = safe_run(["timedatectl", "show"])
    _, localectl_output, _ = safe_run(["localectl", "status"])
    _, selinux_stdout, _ = safe_run(["getenforce"])
    selinux_mode = selinux_stdout.strip().lower()

    return {
        "os": os_info.get("ID", "fedora"),
        "version": os_info.get("VERSION_ID", ""),
        "architecture": architecture.strip(),
        "hostname": hostname.strip(),
        "kernel": kernel.strip(),
        "timezone": parse_timezone(timedatectl_output),
        "locale": parse_locale(localectl_output),
        "selinux": {
            "status": "disabled" if selinux_mode == "disabled" else "enabled",
            "mode": selinux_mode,
        }
    }
