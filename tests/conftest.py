"""Shared pytest fixtures for the MigrateOS test suite."""

import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_manifest():
    """Returns a full manifest dict suitable for generator and bundler testing."""
    return {
        "os_facts": {
            "os": "fedora",
            "version": "41",
            "hostname": "webserver.local",
            "kernel": "6.11.4",
            "architecture": "x86_64",
            "timezone": "UTC",
            "locale": "en_US.UTF-8",
            "selinux": {"status": "enabled", "mode": "enforcing"},
        },
        "packages": {
            "packages": ["nginx"],
            "groups": [],
            "extras": [],
            "custom_repos": [],
        },
        "services": {
            "services": [
                {"name": "nginx.service", "service_tier": "infrastructure", "custom_unit": False},
            ],
        },
        "users": {"users": [], "groups": []},
        "directories": [],
        "configs": {
            "config_files": [],
            "warnings": [],
            "secrets_required": [],
        },
        "cron": {"files": [], "timers": []},
        "sysctl": {"files": []},
        "network": {"connections": [], "warning": None},
        "containers": {"runtimes": [], "running_containers": [], "warning": None},
        "selinux": {"custom_modules": [], "warning": None},
    }
