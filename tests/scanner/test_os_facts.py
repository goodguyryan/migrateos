"""Tests for os_facts.py: OS identity scanning.

TODO:
    - test_parse_os_release_normal() (typical Fedora os-release: ID, VERSION_ID, NAME keys present)
    - test_parse_os_release_quoted_values() (VERSION_ID="41" becomes 41 — quotes stripped)
    - test_parse_os_release_comments_skipped() (lines starting with # are absent from result)
    - test_parse_os_release_empty() (empty string → empty dict)
"""
