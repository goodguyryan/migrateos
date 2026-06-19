"""Scan config files and directories with safety checks and copy method decisions.

Threshold: <=30 files -> copy_method "single"; >30 -> copy_method "directory"
"""

from pathlib import Path
from typing import List, Tuple
import hashlib
from src.utils.paths import (
    is_blocked_path,
    is_excluded_file,
    is_secret_file,
    detect_secrets_in_file,
    detect_includes,
)

def collect_file(config_path: Path) -> dict:
    """Collect metadata for a single config file. Does NOT copy."""
    stat = config_path.stat()

    try:
        data = config_path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
    except (PermissionError, OSError):
        sha = ""

    content = ""
    try:
        content = config_path.read_text(encoding="utf-8", errors="ignore")
    except (PermissionError, OSError, UnicodeDecodeError):
        pass

    lines = content.splitlines()
    preview = "\n".join(lines[:200]) if content else ""

    is_symlink = config_path.is_symlink()
    symlink_target = str(config_path.resolve()) if is_symlink else None

    try:
        bundled_src = config_path.resolve().relative_to(Path("/").resolve()).as_posix()
    except ValueError:
        bundled_src = config_path.name

    return {
        "name": config_path.name,
        "path": str(config_path),
        "bundled_src": bundled_src,
        "owner": str(stat.st_uid),
        "group": str(stat.st_gid),
        "mode": oct(stat.st_mode)[-4:],
        "sha256": sha,
        "size": stat.st_size,
        "preview": preview,
        "secrets_detected": detect_secrets_in_file(content),
        "includes_detected": detect_includes(content),
        "is_symlink": is_symlink,
        "symlink_target": symlink_target,
        "is_secret": is_secret_file(config_path.name),
        "copy_method": "single",
    }

def collect_directory(config_path: Path) -> dict:
    """Collect metadata for a directory tree. Walk all files with safety filters."""
    entries = []
    file_count = 0
    warnings = []

    if not config_path.is_dir():
        return {
            "name": config_path.name,
            "path": str(config_path),
            "entries": [],
            "file_count": 0,
            "copy_method": "single",
            "warnings": ["Not a directory"],
        }

    for item in sorted(config_path.rglob("*")):
        if is_blocked_path(item):
            warnings.append(f"Blocked: {item}")
            continue
        if item.is_file():
            if is_excluded_file(item.name):
                warnings.append(f"Excluded: {item}")
                continue
            file_count += 1
            entries.append(collect_file(item))

    copy_method = "single" if file_count <= 30 else "directory"

    return {
        "name": config_path.name,
        "path": str(config_path),
        "entries": entries,
        "file_count": file_count,
        "copy_method": copy_method,
        "warnings": warnings,
    }

def collect(config_paths: List[Path]) -> Tuple[List[dict], List[str], List[str]]:
    """Orchestrator. Returns (config_files, secrets_required, warnings)."""
    config_files = []
    secrets_required = []
    all_warnings = []

    for path in config_paths:
        if not path.exists():
            all_warnings.append(f"Config path does not exist: {path}")
            continue

        if path.is_dir():
            dir_data = collect_directory(path)
            config_files.append(dir_data)
            all_warnings.extend(dir_data.get("warnings", []))
            for entry in dir_data.get("entries", []):
                if entry.get("secrets_detected"):
                    secrets_required.append(entry["path"])
                if entry.get("is_secret"):
                    secrets_required.append(entry["path"])
                    all_warnings.append(
                        f"Secret file detected (Tier 1): {entry['path']}"
                    )
        else:
            file_data = collect_file(path)
            config_files.append(file_data)
            if file_data.get("secrets_detected"):
                secrets_required.append(str(path))
            if file_data.get("is_secret"):
                secrets_required.append(str(path))
                all_warnings.append(
                    f"Secret file detected (Tier 1): {path}"
                )

    return config_files, secrets_required, all_warnings
