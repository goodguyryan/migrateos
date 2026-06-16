"""Tests for sysctl.py: kernel parameter file scanning.

TODO:
    - test_collect_returns_files_list() (temp_dir with .conf file → file in result)
    - test_collect_skips_non_conf() (.txt file in sysctl.d → not in result)
    - test_collect_handles_missing_dir() (no sysctl.d directory → empty list, no crash)
"""
