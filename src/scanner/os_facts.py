"""Collect OS identity: distribution, kernel, hostname, timezone, locale, SELinux status.

TODO:
    - parse_os_release(text: str = "") -> dict (parse /etc/os-release key=value format)
    - collect() -> dict (orchestrate: os-release, uname -r, uname -m, hostnamectl --static, timedatectl show, localectl status, getenforce)
    - Return structured dict: {os, version, architecture, hostname, kernel, timezone, locale, selinux: {status, mode}}
"""
