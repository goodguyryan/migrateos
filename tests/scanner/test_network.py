"""Tests for network.py: NetworkManager connection scanning."""

from src.scanner.network import parse_nmcli

def test_parse_nmcli_normal():
    text = """\
Wired connection 1:4a8b6c7d-1234-5678-9abc-def012345678:802-3-ethernet:eth0
My VPN:a1b2c3d4-5678-90ab-cdef-1234567890ab:vpn:
"""
    result = parse_nmcli(text)
    assert len(result) == 2
    assert result[0] == {
        "name": "Wired connection 1",
        "uuid": "4a8b6c7d-1234-5678-9abc-def012345678",
        "type": "802-3-ethernet",
        "device": "eth0",
    }
    assert result[1] == {
        "name": "My VPN",
        "uuid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
        "type": "vpn",
        "device": "",
    }

def test_parse_nmcli_empty():
    result = parse_nmcli("")
    assert result == []

def test_parse_nmcli_malformed_line():
    text = "short-line\n"
    result = parse_nmcli(text)
    assert result == []
