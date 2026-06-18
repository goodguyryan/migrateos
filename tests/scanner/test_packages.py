"""Tests for packages.py: DNF package/group/extras/repo scanning."""

from src.scanner.packages import parse_userinstalled, parse_groups, parse_extras

def test_parse_userinstalled_normal():
    """Verify multi-line package list → correct count."""
    text = """\
nginx
python3
git
"""
    result = parse_userinstalled(text)
    assert result == ["nginx", "python3", "git"]


def test_parse_userinstalled_single():
    """Verify one package → list of one."""
    result = parse_userinstalled("nginx\n")
    assert result == ["nginx"]


def test_parse_userinstalled_empty():
    """Verify empty string → empty list."""
    result = parse_userinstalled("")
    assert result == []

def test_parse_groups_dnf4():
    """Verify DNF4 output with Available/Installed headers skipped."""
    text = """\
Installed Groups:
   Development Tools
   Fedora Workstation
Available Groups:
   Container Management
"""
    result = parse_groups(text)
    assert result == ["Development Tools", "Fedora Workstation"]


def test_parse_groups_dnf5():
    """Verify DNF5 output with indented group names parsed."""
    text = """\
  Development Tools
  Fedora Workstation
"""
    result = parse_groups(text)
    assert result == ["Development Tools", "Fedora Workstation"]


def test_parse_groups_empty():
    """Verify empty → empty list."""
    result = parse_groups("")
    assert result == []

def test_parse_extras_normal():
    """Verify multi-line extras, arch suffix stripped."""
    text = """\
Last metadata expiration check: 0:00:03
nginx.x86_64        1.20.1-1.fc41        @System
python3.noarch      3.9.7-1.fc41         @System
"""
    result = parse_extras(text)
    assert result == ["nginx", "python3"]


def test_parse_extras_empty():
    """Verify empty → empty list."""
    result = parse_extras("")
    assert result == []
    