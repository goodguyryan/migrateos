"""Tests for directories.py: app directory metadata and runtime detection."""

from pathlib import Path
from src.scanner.directories import collect

def test_collect_existing_directory(temp_dir):
    """Verify temp_dir with package.json → runtime detected as node."""
    app = temp_dir / "myapp"
    app.mkdir()
    (app / "package.json").write_text("{}")

    result = collect([app])
    assert len(result) == 1
    entry = result[0]
    assert entry["name"] == "myapp"
    assert entry["path"] == str(app)
    assert entry["bundled_src"] == "myapp"
    assert entry["detected_runtime"] == "node"
    assert len(entry["suggested_install_commands"]) > 0
    assert "mode" in entry
    assert "owner" in entry
    assert "group" in entry

def test_collect_missing_directory(temp_dir):
    """Verify nonexistent path → warning entry."""
    missing = Path("/nonexistent/path/xyz")

    result = collect([missing])
    assert len(result) == 1
    assert result[0]["warning"] == "Path does not exist"
    assert result[0]["name"] == "xyz"

def test_collect_empty_directory(temp_dir):
    """Verify dir with no runtime markers → detected_runtime is None."""
    app = temp_dir / "emptyapp"
    app.mkdir()

    result = collect([app])
    assert len(result) == 1
    assert result[0]["detected_runtime"] is None
    assert result[0]["suggested_install_commands"] == []
