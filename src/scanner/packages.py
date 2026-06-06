"""Scan installed packages, groups, extras, and custom repos via DNF.

TODO:
    - _parse_userinstalled(text: str) -> List[str] (one package name per line)
    - _parse_groups(text: str) -> List[str] (strip whitespace, skip header lines)
    - _parse_extras(text: str) -> List[str] (parse dnf list --extras output)
    - _scan_custom_repos() -> List[dict] (scan /etc/yum.repos.d/*.repo, skip stock fedora*.repo)
    - collect() -> dict (use dnf_version.py to get correct commands, orchestrate all queries)
    - DO NOT use dnf history or rpm -qa
    - Return: {packages: [...], groups: [...], extras: [...], custom_repos: [...]}
"""
