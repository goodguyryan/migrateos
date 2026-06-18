"""Scan local users and groups from /etc/passwd and /etc/group.

Filters:
    - UID < 1000 excluded (system accounts)
    - Names in SKIPPED_USERS excluded
    - systemd-* names excluded
    - Only users who own at least one --app-path or --config-path are migrated
    - UID/GID NOT preserved — Ansible assigns new ones
    - SSH keys and sudoers optionally included via flags
"""

from pathlib import Path
from typing import List, Optional
from src.utils.constants import SKIPPED_USERS

def parse_passwd(text: str = None) -> List[dict]:
    if text is None:
        text = Path("/etc/passwd").read_text(encoding="utf-8", errors="ignore")
    users = []
    for line in text.splitlines():
        parts = line.strip().split(":")
        if len(parts) < 7:
            continue
        name = parts[0]
        if name in SKIPPED_USERS or name.startswith("systemd-"):
            continue
        uid_int = int(parts[2])
        if uid_int < 1000:
            continue
        users.append({
            "name": name,
            "uid": uid_int,
            "gid": int(parts[3]),
            "home": parts[5],
            "shell": parts[6],
        })
    return users

def parse_group(text: str = None) -> List[dict]:
    if text is None:
        text = Path("/etc/group").read_text(encoding="utf-8", errors="ignore")
    groups = []
    for line in text.splitlines():
        parts = line.strip().split(":")
        if len(parts) < 4:
            continue
        groups.append({
            "name": parts[0],
            "gid": int(parts[2]),
            "members": parts[3].split(",") if parts[3] else [],
        })
    return groups

def load_authorized_keys(user_home: str) -> Optional[str]:
    key_file = Path(user_home) / ".ssh" / "authorized_keys"
    try:
        return key_file.read_text(encoding="utf-8", errors="ignore") if key_file.is_file() else None
    except (PermissionError, OSError):
        return None

def load_sudoers(username: str) -> Optional[str]:
    sudoers_file = Path("/etc/sudoers.d") / username
    try:
        return sudoers_file.read_text(encoding="utf-8", errors="ignore") if sudoers_file.is_file() else None
    except (PermissionError, OSError):
        return None

def collect(
    app_paths: List[str],
    config_paths: List[str],
    include_ssh_keys: bool = False,
    include_sudoers: bool = False,
) -> dict:
    """Orchestrator. Parse passwd/group, cross-reference ownership, filter."""
    users = parse_passwd()
    groups = parse_group()

    all_paths = [Path(p) for p in app_paths + config_paths]
    owner_names = set()
    for p in all_paths:
        if not p.exists():
            continue
        owner_uid = p.stat().st_uid
        for u in users:
            if u["uid"] == owner_uid:
                owner_names.add(u["name"])

    migrated_users = []
    for u in users:
        if u["name"] not in owner_names:
            continue
        entry = {
            "name": u["name"],
            "home": u["home"],
            "shell": u["shell"],
        }
        if include_ssh_keys:
            keys = load_authorized_keys(u["home"])
            if keys:
                entry["authorized_keys"] = keys
        if include_sudoers:
            sudoers = load_sudoers(u["name"])
            if sudoers:
                entry["sudoers"] = sudoers
        migrated_users.append(entry)

    migrated_user_names = {u["name"] for u in migrated_users}
    migrated_groups = []
    for g in groups:
        if any(m in g["members"] for m in migrated_user_names):
            migrated_groups.append(g)

    return {
        "groups": migrated_groups,
        "users": migrated_users,
    }
