"""Tests for file_collector.py: file copying with safety checks."""

from pathlib import Path
from src.bundler.file_collector import (copy_file_from_disk, 
                                        write_file_from_content,
                                        bundle_config_files,
                                        bundle_custom_repos,
                                        bundle_cron_files)

def test_copy_file_from_disk_copies_successfully(temp_dir):
    """Verify source file copied to dest, content matches, returns (True, 'ok')."""
    src = temp_dir / "nginx.conf"
    src.write_text("server { listen 80; }\n")
    dest = temp_dir / "output" / "nginx.conf"

    ok, reason = copy_file_from_disk(src, dest)

    assert ok is True
    assert reason == "ok"
    assert dest.exists()
    assert dest.read_text() == "server { listen 80; }\n"

def test_copy_file_from_disk_skips_blocked_path():
    """Verify blocked path returns (False, 'blocked: ...')."""
    src = Path("/etc/shadow")
    dest = Path("/tmp/dest_shadow")

    ok, reason = copy_file_from_disk(src, dest)

    assert ok is False
    assert "blocked" in reason

def test_copy_file_from_disk_skips_secret_file(temp_dir):
    """Verify secret filename returns (False, 'secret (Tier 1): ...')."""
    src = temp_dir / "id_rsa"
    src.write_text("-----BEGIN RSA PRIVATE KEY-----\n")
    dest = temp_dir / "output" / "id_rsa"

    ok, reason = copy_file_from_disk(src, dest)

    assert ok is False
    assert "secret (Tier 1)" in reason
    assert not dest.exists()

def test_copy_file_from_disk_warns_on_secret_content(temp_dir):
    """Verify file with PASSWORD= content is copied but flagged."""
    src = temp_dir / "app.conf"
    src.write_text("DB_PASSWORD=mysecret123\n")
    dest = temp_dir / "output" / "app.conf"

    ok, reason = copy_file_from_disk(src, dest)

    assert ok is True
    assert "secrets detected" in reason
    assert dest.exists()
    assert dest.read_text() == "DB_PASSWORD=mysecret123\n"

def test_copy_file_from_disk_missing_source(temp_dir):
    """Verify nonexistent source returns (False, 'error: ...')."""
    src = temp_dir / "nonexistent.conf"
    dest = temp_dir / "output" / "nonexistent.conf"

    ok, reason = copy_file_from_disk(src, dest)

    assert ok is False
    assert "error" in reason

def test_write_file_from_content_writes_successfully(temp_dir):
    """Verify content written to dest, parent dirs created, returns (True, 'ok')."""

    dest = temp_dir / "output" / "etc" / "yum.repos.d" / "custom.repo"
    content = "[custom]\nname=Custom Repo\nbaseurl=https://example.com\n"

    ok, reason = write_file_from_content(content, dest)

    assert ok is True
    assert reason == "ok"
    assert dest.exists()
    assert dest.read_text() == content

def test_bundle_config_files_single(temp_dir):
    """Verify single config entry copied to files/ in output dir."""
    from src.bundler.file_collector import bundle_config_files

    src = temp_dir / "nginx.conf"
    src.write_text("server { listen 80; }\n")
    output_dir = temp_dir / "output"

    config_files = [{
        "name": "nginx.conf",
        "path": str(src),
        "bundled_src": "etc/nginx/nginx.conf",
        "is_secret": False,
        "copy_method": "single",
    }]

    result = bundle_config_files(config_files, output_dir)

    dest = output_dir / "files" / "etc" / "nginx" / "nginx.conf"
    assert dest.exists()
    assert dest.read_text() == "server { listen 80; }\n"
    assert len(result["copied"]) == 1
    assert len(result["skipped"]) == 0

def test_bundle_config_files_directory(temp_dir):
    """Verify directory entry copies each sub-file individually."""
    from src.bundler.file_collector import bundle_config_files

    src_dir = temp_dir / "sshd_config.d"
    src_dir.mkdir()
    (src_dir / "50-custom.conf").write_text("Port 2222\n")
    (src_dir / "60-hardening.conf").write_text("MaxAuthTries 3\n")
    output_dir = temp_dir / "output"

    config_files = [{
        "name": "sshd_config.d",
        "path": str(src_dir),
        "copy_method": "directory",
        "entries": [
            {
                "name": "50-custom.conf",
                "path": str(src_dir / "50-custom.conf"),
                "bundled_src": "etc/ssh/sshd_config.d/50-custom.conf",
                "is_secret": False,
                "copy_method": "single",
            },
            {
                "name": "60-hardening.conf",
                "path": str(src_dir / "60-hardening.conf"),
                "bundled_src": "etc/ssh/sshd_config.d/60-hardening.conf",
                "is_secret": False,
                "copy_method": "single",
            },
        ],
    }]

    result = bundle_config_files(config_files, output_dir)

    assert (output_dir / "files" / "etc" / "ssh" / "sshd_config.d" / "50-custom.conf").exists()
    assert (output_dir / "files" / "etc" / "ssh" / "sshd_config.d" / "60-hardening.conf").exists()
    assert len(result["copied"]) == 2
    assert len(result["skipped"]) == 0

def test_bundle_config_files_skips_secret_entries(temp_dir):
    """Verify is_secret: True entries are not copied."""

    src = temp_dir / "id_rsa"
    src.write_text("-----BEGIN RSA PRIVATE KEY-----\n")
    output_dir = temp_dir / "output"

    config_files = [{
        "name": "id_rsa",
        "path": str(src),
        "bundled_src": "etc/ssh/id_rsa",
        "is_secret": True,
        "copy_method": "single",
    }]

    result = bundle_config_files(config_files, output_dir)

    assert not (output_dir / "files" / "etc" / "ssh" / "id_rsa").exists()
    assert len(result["copied"]) == 0
    assert len(result["skipped"]) == 1
    assert "secret (Tier 1)" in result["skipped"][0]

def test_bundle_custom_repos_writes_content(temp_dir):
    """Verify repo content written to files/etc/yum.repos.d/."""

    output_dir = temp_dir / "output"
    custom_repos = [{
        "name": "rpmfusion-free",
        "filename": "rpmfusion-free.repo",
        "content": "[rpmfusion-free]\nname=RPM Fusion Free\n",
    }]

    result = bundle_custom_repos(custom_repos, output_dir)

    dest = output_dir / "files" / "etc" / "yum.repos.d" / "rpmfusion-free.repo"
    assert dest.exists()
    assert dest.read_text() == "[rpmfusion-free]\nname=RPM Fusion Free\n"
    assert len(result["copied"]) == 1
    assert len(result["skipped"]) == 0

def test_bundle_cron_files_writes_content(temp_dir):
    """Verify cron content written to files/{dest}."""

    output_dir = temp_dir / "output"
    cron_files = [{
        "src": "/etc/cron.d/backup.sh",
        "dest": "cron.d/backup.sh",
        "content": "#!/bin/bash\necho backup\n",
    }]

    result = bundle_cron_files(cron_files, output_dir)

    dest = output_dir / "files" / "cron.d" / "backup.sh"
    assert dest.exists()
    assert dest.read_text() == "#!/bin/bash\necho backup\n"
    assert len(result["copied"]) == 1
    assert len(result["skipped"]) == 0
