"""Tests for paths.py: include directive scanning in config files.

TODO:
    - test_scan_includes_nginx() (include directive)
    - test_scan_includes_apache() (Include directive)
    - test_scan_includes_sshd() (Include directive)
    - test_scan_includes_sudoers() (#includedir directive)
    - test_scan_includes_syslog() ($IncludeConfig directive)
    - test_scan_includes_systemd() (.include directive)
    - test_scan_includes_none() (no includes)
    - test_scan_includes_no_false_positives() (regular text that looks like include)
"""
