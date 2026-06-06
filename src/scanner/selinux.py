"""Scan SELinux status and custom modules.

TODO:
    - collect() -> dict
    - Run: getenforce, sestatus, semodule -l
    - Detect custom (non-stock) SELinux modules by comparing against known stock list
    - Warn if custom modules detected (they cannot be auto-migrated)
    - Return: {status, mode, custom_modules: [...], warning: Optional[str]}
"""
