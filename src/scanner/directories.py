"""Scan app directories for metadata: ownership, mode, runtime detection, install suggestions.

Does NOT copy files — bundler handles that.
"""

from pathlib import Path
from typing import List
from src.utils.paths import detect_runtime, suggest_install


def collect(app_paths: List[Path]) -> List[dict]:
    results = []
    for path in app_paths:
        if not path.exists():
            results.append({
                "name": path.name,
                "path": str(path),
                "warning": "Path does not exist",
            })
            continue

        stat = path.stat()
        runtime = detect_runtime(path)

        try:
            import pwd
            owner = pwd.getpwuid(stat.st_uid).pw_name
        except ImportError:
            owner = str(stat.st_uid)

        try:
            import grp
            group = grp.getgrgid(stat.st_gid).gr_name
        except ImportError:
            group = str(stat.st_gid)

        results.append({
            "name": path.name,
            "path": str(path),
            "bundled_src": path.name,
            "owner": owner,
            "group": group,
            "mode": oct(stat.st_mode)[-4:],
            "detected_runtime": runtime,
            "suggested_install_commands": suggest_install(runtime) if runtime else [],
        })

    return results
