"""Detect running Docker and Podman containers — warning only, no auto-migration.

TODO:
    - collect() -> dict
    - Run: docker ps --format and podman ps --format (ignore failures gracefully)
    - Return: {runtimes: [...], running_containers: [...], warning: Optional[str]}
"""
