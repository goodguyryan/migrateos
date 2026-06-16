"""Tests for packages.py: DNF package/group/extras/repo scanning.

TODO:
    - test_parse_userinstalled_normal() (multi-line package list → correct count)
    - test_parse_userinstalled_single() (one package → list of one)
    - test_parse_userinstalled_empty() (empty string → empty list)
    - test_parse_groups_dnf4() (DNF4 output with Available/Installed headers skipped)
    - test_parse_groups_dnf5() (DNF5 output with indented group names parsed)
    - test_parse_groups_empty() (empty → empty list)
    - test_parse_extras_normal() (multi-line extras, arch suffix .x86_64 stripped)
    - test_parse_extras_empty() (empty → empty list)
"""
