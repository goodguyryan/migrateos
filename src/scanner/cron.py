"""Scan cron files and systemd timers."""

from pathlib import Path
from typing import List
from src.utils.command import safe_run
from src.utils.paths import is_blocked_path, is_excluded_file

def scan_cron_dirs(cron_base: Path = Path("/etc")) -> List[dict]:
    results = []
    cron_dirs = [
        cron_base / "cron.d",
        cron_base / "cron.hourly",
        cron_base / "cron.daily",
        cron_base / "cron.weekly",
        cron_base / "cron.monthly",
    ]
    for cron_dir in cron_dirs:
        if not cron_dir.is_dir():
            continue
        for item in sorted(cron_dir.iterdir()):
            if not item.is_file():
                continue
            if is_blocked_path(item) or is_excluded_file(item.name):
                continue
            results.append({
                "src": str(item),
                "dest": item.relative_to(cron_base).as_posix(),
                "content": item.read_text(encoding="utf-8", errors="ignore"),
            })
    return results

def scan_systemd_timers(systemd_base: Path = Path("/etc/systemd/system")) -> List[dict]:
    timers = []
    if systemd_base.is_dir():
        for timer_file in sorted(systemd_base.glob("*.timer")):
            if is_blocked_path(timer_file):
                continue
            ok, _, _ = safe_run(["systemctl", "is-enabled", timer_file.name])
            timers.append({
                "name": timer_file.stem,
                "enabled": ok,
            })
    return timers

def collect() -> dict:
    return {
        "files": scan_cron_dirs(),
        "timers": scan_systemd_timers(),
    }