"""Tests for network.py: NetworkManager connection scanning.

TODO:
    - test_parse_nmcli_normal() (terse nmcli output → correct connection dicts)
    - test_parse_nmcli_empty() (empty → empty list)
    - test_parse_nmcli_malformed_line() (short line <4 fields → skipped)
"""
