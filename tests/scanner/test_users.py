"""Tests for users.py: /etc/passwd and /etc/group parsing."""

from src.scanner.users import parse_passwd, parse_group

def test_parse_passwd_normal():
    """Verify valid passwd line → user dict with all fields."""
    text = "myapp:x:1001:1001:My App:/opt/myapp:/bin/bash\n"
    result = parse_passwd(text)
    assert len(result) == 1
    assert result[0] == {
        "name": "myapp",
        "uid": 1001,
        "gid": 1001,
        "home": "/opt/myapp",
        "shell": "/bin/bash",
    }

def test_parse_passwd_skips_system_uid():
    """Verify UID < 1000 → excluded."""
    text = "testuser:x:500:500:Test:/home/testuser:/bin/sh\n"
    result = parse_passwd(text)
    assert result == []

def test_parse_passwd_skips_skip_list():
    """Verify names in SKIPPED_USERS → excluded."""
    text = """\
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
"""
    result = parse_passwd(text)
    assert result == []

def test_parse_passwd_skips_systemd_prefix():
    """Verify names starting with systemd- → excluded."""
    text = "systemd-timesync:x:996:996:systemd Time Sync:/:/usr/sbin/nologin\n"
    result = parse_passwd(text)
    assert result == []

def test_parse_passwd_malformed():
    """Verify incomplete line (<7 fields) → skipped."""
    text = "short:x:1001\n"
    result = parse_passwd(text)
    assert result == []

def test_parse_group_normal():
    """Verify valid group line → correct dict."""
    text = "myapp:x:1001:\n"
    result = parse_group(text)
    assert len(result) == 1
    assert result[0] == {"name": "myapp", "gid": 1001, "members": []}

def test_parse_group_with_members():
    """Verify comma-separated members → split into list."""
    text = "developers:x:1002:alice,bob,charlie\n"
    result = parse_group(text)
    assert result[0]["members"] == ["alice", "bob", "charlie"]