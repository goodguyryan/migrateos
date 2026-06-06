"""Scan cron files and systemd timers.

TODO:
    - _scan_cron_dirs() -> List[dict] (scan /etc/cron.d/, /etc/cron.{hourly,daily,weekly,monthly}/)
    - _scan_systemd_timers() -> List[dict] (scan /etc/systemd/system/*.timer)
    - collect() -> dict
    - Return: {files: [{src, dest, content}], timers: [{name, enabled}]}
"""
