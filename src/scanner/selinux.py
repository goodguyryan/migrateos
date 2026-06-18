"""Scan SELinux status and custom modules.

TODO:
    - collect() -> dict
    - Run: getenforce, sestatus, semodule -l
    - Detect custom (non-stock) SELinux modules by comparing against known stock list
    - Warn if custom modules detected (they cannot be auto-migrated)
    - Return: {status, mode, custom_modules: [...], warning: Optional[str]}
"""
from src.utils.command import safe_run
from src.utils.constants import STOCK_SELINUX_MODULES

def parse_getenforce(text: str) -> dict:
    mode = text.strip().lower()
    return {
        "status": "disabled" if mode == "disabled" else "enabled",
        "mode": mode,
    }

def parse_sestatus(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip().lower()] = value.strip()
    return result

def parse_semodule(text: str) -> dict:
    modules = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            modules.append(line.split()[0])
    custom = [m for m in modules if m not in STOCK_SELINUX_MODULES]
    return {
        "all_modules": modules,
        "custom_modules": custom,
        "warning": (
            "Custom SELinux modules detected and cannot be auto-migrated"
            if custom else None
        ),
    }

def collect() -> dict:
    _, enforcing_out, _ = safe_run(["getenforce"])
    _, sestatus_out, _ = safe_run(["sestatus"])
    _, modules_out, _ = safe_run(["semodule", "-l"])

    enforcing = parse_getenforce(enforcing_out)
    sestatus = parse_sestatus(sestatus_out)
    modules = parse_semodule(modules_out)

    return {
        "status": enforcing["status"],
        "mode": enforcing["mode"],
        "sestatus": sestatus,
        "custom_modules": modules["custom_modules"],
        "warning": modules["warning"],
    }
