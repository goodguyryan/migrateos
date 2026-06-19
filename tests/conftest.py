"""Shared pytest fixtures for the MigrateOS test suite.

TODO:
    - Fixture sample_manifest() -> dict (complete minimal manifest exercising all sections: os, packages, services, users, configs, firewalld, cron, sysctl, secrets, warnings, databases, containers, network)
    - Fixture temp_dir() -> Path (creates temporary directory, yields it, cleans up after test)
"""

import tempfile
from pathlib import Path
import pytest

@pytest.fixture
def temp_dir():
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as tmpdir:
        yield Path(tmpdir)
