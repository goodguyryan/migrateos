"""Tests for sysctl.py: kernel parameter file scanning."""

from src.scanner.sysctl import collect

def test_collect_returns_files_list(temp_dir):
    """Verify temp_dir with .conf file in sysctl.d → file found in result."""
    d = temp_dir / "sysctl.d"
    d.mkdir()
    (d / "custom.conf").write_text("net.ipv4.ip_forward=1")

    result = collect(temp_dir)
    assert len(result["files"]) == 1
    assert result["files"][0]["src"] == str(d / "custom.conf")
    assert result["files"][0]["dest"] == "sysctl.d/custom.conf"

def test_collect_skips_non_conf(temp_dir):
    """Verify .txt file in sysctl.d → not in result."""
    d = temp_dir / "sysctl.d"
    d.mkdir()
    (d / "notes.txt").write_text("some notes")

    result = collect(temp_dir)
    assert len(result["files"]) == 0

def test_collect_handles_missing_dir(temp_dir):
    """Verify no sysctl.d directory → empty list, no crash."""
    result = collect(temp_dir)
    assert result == {"files": []}

def test_collect_includes_sysctl_conf(temp_dir):
    """Verify /etc/sysctl.conf → included when present."""
    (temp_dir / "sysctl.conf").write_text("fs.file-max=65535")
    d = temp_dir / "sysctl.d"
    d.mkdir()
    (d / "custom.conf").write_text("key=val")

    result = collect(temp_dir)
    assert len(result["files"]) == 2
    dests = {f["dest"] for f in result["files"]}
    assert dests == {"sysctl.conf", "sysctl.d/custom.conf"}
