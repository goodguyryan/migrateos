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

@pytest.fixture
def mock_scanners():
    """Patch all 11 scanner collect() functions to return controlled test data."""
    from unittest.mock import patch
    patches = [
        patch("src.scanner.os_facts.collect", return_value={
            "os": "fedora", "version": "41", "architecture": "x86_64",
            "hostname": "testserver", "kernel": "6.11.4",
            "timezone": "UTC", "locale": "en_US.UTF-8",
            "selinux": {"status": "enabled", "mode": "enforcing"},
        }),
        patch("src.scanner.packages.collect", return_value={
            "packages": ["nginx", "postgresql"],
            "groups": ["server-product-environment"],
            "extras": ["htop"],
            "custom_repos": [{"name": "mypkgrepo", "filename": "mypkgrepo.repo", "content": "[mypkgrepo]"}],
        }),
        patch("src.scanner.services.collect", return_value={
            "services": [{
                "name": "nginx.service", "enabled": True, "state": "running",
                "custom_unit": False, "unit_file": None, "environment_files": [],
                "timer_activated": False, "socket_activated": False,
                "service_tier": "infrastructure",
            }],
        }),
        patch("src.scanner.users.collect", return_value={
            "users": [{"name": "deploy", "home": "/home/deploy", "shell": "/bin/bash"}],
            "groups": [{"name": "deploy", "gid": 1001, "members": ["deploy"]}],
        }),
        patch("src.scanner.directories.collect", return_value=[
            {"name": "www", "path": "/var/www", "bundled_src": "www",
             "owner": "deploy", "group": "deploy", "mode": "0755",
             "detected_runtime": "node", "suggested_install_commands": ["npm install"]},
        ]),
        patch("src.scanner.configs.collect", return_value=(
            [{"name": "nginx.conf", "path": "/etc/nginx/nginx.conf",
              "bundled_src": "etc/nginx/nginx.conf", "owner": "root", "group": "root",
              "mode": "0644", "sha256": "abc123", "size": 256,
              "preview": "# nginx config", "secrets_detected": [],
              "includes_detected": [], "is_symlink": False,
              "symlink_target": None, "is_secret": False, "copy_method": "file"}],
            [],
            [],
        )),
        patch("src.scanner.cron.collect", return_value={
            "files": [{"src": "/etc/cron.d/backup", "dest": "cron.d/backup", "content": "0 * * * * root /usr/bin/backup.sh"}],
            "timers": [],
        }),
        patch("src.scanner.selinux.collect", return_value={
            "status": "enabled", "mode": "enforcing",
            "sestatus": {"SELinux status": "enabled"},
            "custom_modules": [], "warning": None,
        }),
        patch("src.scanner.network.collect", return_value={
            "connections": [], "custom_connections": [], "warning": None,
        }),
        patch("src.scanner.sysctl.collect", return_value={
            "files": [{"src": "/etc/sysctl.conf", "dest": "sysctl.conf"}],
        }),
        patch("src.scanner.containers.collect", return_value={
            "runtimes": [], "running_containers": [], "warning": None,
        }),
    ]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()
