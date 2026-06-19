"""Collect and copy files from source server into output directory with safety checks.

TODO:
    - Implement collect_file(src: Path, dest_dir: Path) -> Tuple[bool, str] (uses shutil.copy2, returns success+reason)
    - Implement collect_directory(src_dir: Path, dest_dir: Path) -> Tuple[List[Path], List[str], List[str]]
      (recursive walk, applies is_blocked() + is_excluded() + detect_secrets() to every file)
    - Create destination subdirectories as needed
    - Skip blocked/excluded files, flag secrets
    - Return: (copied_paths, warnings, skipped_secrets)
"""
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

def write_file_from_content(content: str, dest_path: str) -> Tuple[bool, str]:
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
