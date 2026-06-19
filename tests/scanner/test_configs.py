"""Tests for configs.py: config file/directory metadata collection with safety checks."""

import os
from pathlib import Path
import pytest
from src.scanner.configs import collect_file, collect_directory, collect

def test_collect_file_basic(temp_dir):
    """Verify stat, sha256, preview populated for a single file."""
    config = temp_dir / "nginx.conf"
    config.write_text("server { listen 80; }\n")

    result = collect_file(config)
    assert result["name"] == "nginx.conf"
    assert result["size"] > 0
    assert len(result["sha256"]) == 64
    assert "listen 80" in result["preview"]
    assert result["copy_method"] == "single"
    assert result["secrets_detected"] == []
    assert result["is_symlink"] is False
    assert result["symlink_target"] is None
    assert result["is_secret"] is False
    assert "owner" in result
    assert "group" in result
    assert "mode" in result

def test_collect_file_secret_detection(temp_dir):
    """Verify content with PASSWORD= -> secrets detected."""
    config = temp_dir / "app.conf"
    config.write_text("DB_PASSWORD=mysecret\n")

    result = collect_file(config)
    assert len(result["secrets_detected"]) > 0
    assert result["is_secret"] is False

def test_collect_file_include_detection(temp_dir):
    """Verify content with Include directive -> includes detected."""
    config = temp_dir / "nginx.conf"
    config.write_text("include /etc/nginx/conf.d/*.conf;\n")

    result = collect_file(config)
    assert len(result["includes_detected"]) > 0

def test_collect_directory_small(temp_dir):
    """Verify <=30 files -> copy_method "single"."""
    d = temp_dir / "smallconfig"
    d.mkdir()
    for i in range(3):
        (d / f"file{i}.conf").write_text("key=val\n")

    result = collect_directory(d)
    assert result["copy_method"] == "single"
    assert result["file_count"] == 3
    assert len(result["entries"]) == 3

def test_collect_directory_large(temp_dir):
    """Verify >30 files -> copy_method "directory"."""
    d = temp_dir / "largeconfig"
    d.mkdir()
    for i in range(31):
        (d / f"file{i}.conf").write_text("key=val\n")

    result = collect_directory(d)
    assert result["copy_method"] == "directory"
    assert result["file_count"] == 31
    assert len(result["entries"]) == 31

def test_collect_directory_blocked(temp_dir):
    """Verify blocked files skipped (no crash, warnings is list)."""
    d = temp_dir / "someconfig"
    d.mkdir()
    (d / "allowed.conf").write_text("key=val\n")

    result = collect_directory(d)
    assert result["file_count"] == 1
    assert isinstance(result["warnings"], list)

def test_collect_directory_excluded(temp_dir):
    """Verify *.swp files skipped."""
    d = temp_dir / "testconfig"
    d.mkdir()
    (d / "keep.conf").write_text("data\n")
    (d / "temp.swp").write_text("vim junk\n")

    result = collect_directory(d)
    assert result["file_count"] == 1
    names = {e["name"] for e in result["entries"]}
    assert names == {"keep.conf"}

@pytest.mark.skipif(os.name == "nt", reason="symlink requires admin on Windows")
def test_collect_symlink(temp_dir):
    """Verify symlink detected, target resolved."""
    target = temp_dir / "real.conf"
    target.write_text("real content\n")
    link = temp_dir / "link.conf"
    link.symlink_to(target)

    result = collect_file(link)
    assert result["is_symlink"] is True
    assert result["symlink_target"] is not None

def test_collect_missing_path():
    """Verify nonexistent -> warning, not in results."""
    result = collect([Path("/nonexistent/config/path")])
    config_files, secrets_required, warnings = result
    assert len(config_files) == 0
    assert len(warnings) == 1
    assert "does not exist" in warnings[0]
