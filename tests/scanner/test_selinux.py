"""Tests for selinux.py: SELinux status and module scanning.

TODO:
    - test_parse_getenforce_enforcing() ("Enforcing\n" → status enabled, mode enforcing)
    - test_parse_getenforce_disabled() ("Disabled\n" → status disabled)
    - test_parse_semodule_output() (multiline module list → correct count of modules)
"""
