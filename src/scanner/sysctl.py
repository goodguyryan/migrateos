"""Scan kernel parameters from sysctl config files."""

from pathlib import Path
from src.utils.paths import is_excluded_file, is_blocked_path

def collect(sysctl_dir: Path = Path("/etc")) -> dict:
    files = []
    
    conf = sysctl_dir / "sysctl.conf"
    if conf.is_file() and not is_blocked_path(conf):
        files.append({"src": str(conf), "dest": "sysctl.conf"})

    sysctl_d_dir = sysctl_dir / "sysctl.d"
    if sysctl_d_dir.is_dir():
        for items in sorted(sysctl_d_dir.glob("*.conf")):
            if items.is_file() and not is_blocked_path(items) and not is_excluded_file(items.name):
                files.append({"src": str(items), "dest": items.relative_to(sysctl_dir).as_posix()})

    return {"files": files}
