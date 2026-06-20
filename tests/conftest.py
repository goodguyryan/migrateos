"""Shared pytest fixtures for the MigrateOS test suite."""

import tempfile
from pathlib import Path
import pytest

@pytest.fixture
def temp_dir():
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_manifest():
    """Returns a minimal manifest dict suitable for bundler testing."""
    return {
        "configs": {
            "config_files": [],
            "warnings": [],
        },
        "packages": {
            "custom_repos": [],
        },
        "cron": {
            "files": [],
        },
        "sysctl": {
            "files": [],
        },
        "services": {
            "services": [],
        },
        "network": {
            "connections": [],
        },
    }
