"""Tests for os_facts.py: OS identity scanning."""

from src.scanner.os_facts import parse_os_release, parse_timezone, parse_locale

def test_parse_os_release_normal():
    """Verify typical Fedora os-release: ID, VERSION_ID, NAME keys present."""
    text = """\
ID=fedora
VERSION_ID=41
NAME=Fedora Linux
"""
    result = parse_os_release(text)
    assert result["ID"] == "fedora"
    assert result["VERSION_ID"] == "41"
    assert result["NAME"] == "Fedora Linux"


def test_parse_os_release_quoted_values():
    """Verify quoted values have quotes stripped."""
    text = """\
ID="fedora"
VERSION_ID="41"
PRETTY_NAME='Fedora 41'
"""
    result = parse_os_release(text)
    assert result["ID"] == "fedora"
    assert result["VERSION_ID"] == "41"
    assert result["PRETTY_NAME"] == "Fedora 41"


def test_parse_os_release_comments_skipped():
    """Verify lines starting with # are absent from result."""
    text = """\
# This is a comment
ID=fedora
# Another comment
VERSION_ID=41
"""
    result = parse_os_release(text)
    assert "# This is a comment" not in result
    assert "# Another comment" not in result
    assert result["ID"] == "fedora"
    assert result["VERSION_ID"] == "41"


def test_parse_os_release_empty():
    """Verify empty string returns empty dict."""
    result = parse_os_release("")
    assert result == {}


def test_parse_timezone_normal():
    """Verify timezone extracted from timedatectl show output."""
    text = """\
Timezone=America/New_York
LocalRTC=no
CanNTP=yes
"""
    result = parse_timezone(text)
    assert result == "America/New_York"


def test_parse_timezone_missing():
    """Verify empty string returned when Timezone key not present."""
    result = parse_timezone("LocalRTC=no\nCanNTP=yes\n")
    assert result == ""


def test_parse_timezone_empty():
    """Verify empty string returned for empty input."""
    result = parse_timezone("")
    assert result == ""


def test_parse_locale_normal():
    """Verify locale extracted from localectl status output."""
    text = """\
   System Locale: LANG=en_US.UTF-8
       VC Keymap: us
"""
    result = parse_locale(text)
    assert result == "en_US.UTF-8"


def test_parse_locale_missing():
    """Verify empty string returned when LANG= not present."""
    result = parse_locale("VC Keymap: us\nX11 Layout: us\n")
    assert result == ""


def test_parse_locale_empty():
    """Verify empty string returned for empty input."""
    result = parse_locale("")
    assert result == ""
