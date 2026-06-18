"""Scan installed packages, groups, extras, and custom repos via DNF."""

from pathlib import Path
from typing import List
from src.utils.command import safe_run
from src.utils.dnf_utils import (detect_dnf_version,
                                 return_userinstalled_cmd,
                                 return_group_list_cmd,
                                 return_extras_cmd)

def parse_userinstalled(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]

def parse_groups(text: str) -> List[str]:
    groups = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Available"):
            break
        if line.startswith("Installed"):
            continue
        groups.append(line.lstrip())
    return groups

def parse_extras(text: str) -> List[str]:
    packages = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("Last metadata") or line.startswith("Available"):
            continue
        parts = line.split()
        if parts:
            packages.append(parts[0].rsplit(".", 1)[0])
    return packages

def scan_custom_repos() -> List[dict]:
    stock = {"fedora.repo", "fedora-updates.repo", "fedora-modular.repo"}
    repos_dir = Path("/etc/yum.repos.d")
    custom = []
    if repos_dir.is_dir():
        for repo_file in sorted(repos_dir.glob("*.repo")):
            if repo_file.name in stock:
                continue
            custom.append({
                "name": repo_file.stem,
                "filename": repo_file.name,
                "content": repo_file.read_text(encoding="utf-8", errors="ignore"),
            })
    return custom


def collect() -> dict:
    dnf_cmd = detect_dnf_version()
    _, userinstalled_out, _ = safe_run(return_userinstalled_cmd(dnf_cmd))
    _, groups_out, _ = safe_run(return_group_list_cmd(dnf_cmd))
    _, extras_out, _ = safe_run(return_extras_cmd(dnf_cmd))
    custom_repos = scan_custom_repos()

    return {
        "packages": parse_userinstalled(userinstalled_out),
        "groups": parse_groups(groups_out),
        "extras": parse_extras(extras_out),
        "custom_repos": custom_repos
    }
