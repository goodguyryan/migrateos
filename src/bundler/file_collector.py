"""Bundler — copies files from source server into output directory with safety checks."""
import shutil
from pathlib import Path
from typing import List, Tuple
from src.utils.paths import is_blocked_path, is_excluded_file, is_secret_file, detect_secrets_in_file

def copy_file_from_disk(src_path: Path, dest_path: Path) -> Tuple[bool, str]:
    if is_blocked_path(src_path):
        return (False, f"blocked: {src_path}")
    if is_excluded_file(src_path.name):
        return (False, f"excluded: {src_path}")
    if is_secret_file(src_path.name):
        return (False, f"secret (Tier 1): {src_path}")
    
    secrets_warning = ""
    try:
        content = src_path.read_text(encoding="utf-8", errors="ignore")
        found = detect_secrets_in_file(content)
        if found:
            secrets_warning = f"secrets detected: {', '.join(found)}"
    except (PermissionError, OSError, UnicodeDecodeError):
        pass
    
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_path)
        if secrets_warning:
          return (True, f"ok: {secrets_warning}")
        return (True, "ok")
    except (PermissionError, OSError, shutil.Error) as e:
        return (False, f"error: {e}")

def write_file_from_content(content: str, dest_path: Path) -> Tuple[bool, str]:
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(content, encoding="utf-8")
        return (True, "ok")
    except (PermissionError, OSError) as e:
        return (False, f"error: {e}")

def bundle_config_files(config_files: List[dict], output_dir: Path) -> dict:
    copied = []
    skipped = []

    for config_file in config_files:
        if config_file.get("copy_method") == "directory":
            for file_entry in config_file.get("entries", []):
                if file_entry.get("is_secret"):
                    skipped.append(f"secret (Tier 1): {file_entry['path']}")
                    continue
                src = Path(file_entry["path"])
                dest = output_dir / "files" / file_entry["bundled_src"]
                ok, reason = copy_file_from_disk(src, dest)
                
                if ok:
                    copied.append(str(dest.relative_to(output_dir)))
                else:
                    skipped.append(reason)

        elif config_file.get("is_secret"):
            skipped.append(f"secret (Tier 1): {config_file['path']}")
      
        else:
            src = Path(config_file["path"])
            dest = output_dir / "files" / config_file["bundled_src"]
            ok, reason = copy_file_from_disk(src, dest)
            
            if ok:
                copied.append(str(dest.relative_to(output_dir)))
            else:
                skipped.append(reason)
    
    return {"copied": copied, "skipped": skipped}

def bundle_custom_repos(custom_repos: List[dict], output_dir: Path) -> dict:
    copied = []
    skipped = []

    for repo in custom_repos:
        dest = output_dir / "files" / "etc" / "yum.repos.d" / repo["filename"]
        ok, reason = write_file_from_content(repo["content"], dest)
        
        if ok:
            copied.append(f"files/etc/yum.repos.d/{repo['filename']}")
        else:
            skipped.append(reason)
    
    return {"copied": copied, "skipped": skipped}

def bundle_cron_files(cron_files: List[dict], output_dir: Path) -> dict:
    copied = []
    skipped = []

    for cron_file in cron_files:
        dest = output_dir / "files" / cron_file["dest"]
        ok, reason = write_file_from_content(cron_file["content"], dest)

        if ok:
            copied.append(f"files/{cron_file['dest']}")
        else:
            skipped.append(reason)

    return {"copied": copied, "skipped": skipped}

def bundle_sysctl_files(sysctl_files: List[dict], output_dir: Path) -> dict:
    copied = []
    skipped = []

    for sysctl_file in sysctl_files:
        src = Path(sysctl_file["src"])
        dest = output_dir / "files" /sysctl_file["dest"]
        ok, reason = copy_file_from_disk(src, dest)

        if ok:
            copied.append(f"files/{sysctl_file['dest']}")
        else:
            skipped.append(reason)

    return {"copied": copied, "skipped": skipped}

def bundle_services(services: List[dict], output_dir: Path) -> dict:
    copied = []
    skipped = []

    for service in services:
        if not service.get("custom_unit"):
            continue
        if not service.get("unit_file"):
            skipped.append(f"no unit_file content: {service['name']}")
            continue

        dest = output_dir / "files" / "systemd" / service["name"]
        ok, reason = write_file_from_content(service["unit_file"], dest)

        if ok:
            copied.append(f"files/systemd/{service['name']}")
        else:
            skipped.append(reason)
    
    return {"copied": copied, "skipped": skipped}

def bundle_network_files(output_dir: Path) -> dict:
    copied = []
    skipped = []

    NetworkManager_dir = Path("/etc/NetworkManager/system-connections")
    if not NetworkManager_dir.is_dir():
        return {"copied": [], "skipped": ["NetworkManager connections dir not found"]}

    for NetworkManager_file in sorted(NetworkManager_dir.glob("*.nmconnection")):
        if is_blocked_path(NetworkManager_file):
            skipped.append(f"blocked: {NetworkManager_file}")
            continue

        dest = output_dir / "review" / "NetworkManager" / NetworkManager_file.name
        ok, reason = copy_file_from_disk(NetworkManager_file, dest)
        if ok:
            copied.append(str(dest.relative_to(output_dir)))
        else:
            skipped.append(reason)

    return {"copied": copied, "skipped": skipped}

def bundle_manifest(manifest: dict, output_dir: Path, include_network: bool = False) -> dict:
    all_copied = []
    all_skipped = []
    all_warnings = []

    config_files = manifest.get("configs", {}).get("config_files", [])
    result = bundle_config_files(config_files, output_dir)
    all_copied.extend(result["copied"])
    all_skipped.extend(result["skipped"])
    all_warnings.extend(manifest.get("configs", {}).get("warnings", []))

    custom_repos = manifest.get("packages", {}).get("custom_repos", [])
    result = bundle_custom_repos(custom_repos, output_dir)
    all_copied.extend(result["copied"])
    all_skipped.extend(result["skipped"])

    cron_files = manifest.get("cron", {}).get("files", [])
    result = bundle_cron_files(cron_files, output_dir)
    all_copied.extend(result["copied"])
    all_skipped.extend(result["skipped"])

    sysctl_files = manifest.get("sysctl", {}).get("files", [])
    result = bundle_sysctl_files(sysctl_files, output_dir)
    all_copied.extend(result["copied"])
    all_skipped.extend(result["skipped"])

    services = manifest.get("services", {}).get("services", [])
    result = bundle_services(services, output_dir)
    all_copied.extend(result["copied"])
    all_skipped.extend(result["skipped"])

    if include_network:
        result = bundle_network_files(output_dir)
        all_copied.extend(result["copied"])
        all_skipped.extend(result["skipped"])

    if all_skipped:
        all_warnings.append(
            f"{len(all_skipped)} file(s) skipped during bundling. "
            "Review the skipped list for blocked/secret files."
        )

    return {
        "copied": all_copied,
        "skipped": all_skipped,
        "warnings": all_warnings,
    }
