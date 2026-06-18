"""Tests for selinux.py: SELinux status and module scanning."""

from src.scanner.selinux import parse_getenforce, parse_sestatus, parse_semodule

def test_parse_getenforce_enforcing():
    result = parse_getenforce("Enforcing\n")
    assert result == {"status": "enabled", "mode": "enforcing"}

def test_parse_getenforce_permissive():
    result = parse_getenforce("Permissive\n")
    assert result == {"status": "enabled", "mode": "permissive"}

def test_parse_getenforce_disabled():
    result = parse_getenforce("Disabled\n")
    assert result == {"status": "disabled", "mode": "disabled"}

def test_parse_sestatus_normal():
    text = """\
SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
"""
    result = parse_sestatus(text)
    assert result["selinux status"] == "enabled"
    assert result["selinuxfs mount"] == "/sys/fs/selinux"
    assert result["loaded policy name"] == "targeted"
    assert result["current mode"] == "enforcing"
    assert result["mode from config file"] == "enforcing"

def test_parse_sestatus_empty():
    result = parse_sestatus("")
    assert result == {}

def test_parse_semodule_normal():
    text = """\
abrt        1.0
ssh         2.0
cockpit     3.0
"""
    result = parse_semodule(text)
    assert result["all_modules"] == ["abrt", "ssh", "cockpit"]
    assert result["custom_modules"] == []

def test_parse_semodule_custom_detection():
    text = "myapp  1.0\n"
    result = parse_semodule(text)
    assert result["custom_modules"] == ["myapp"]
    assert result["warning"] is not None

def test_parse_semodule_empty():
    result = parse_semodule("")
    assert result == {"all_modules": [], "custom_modules": [], "warning": None}