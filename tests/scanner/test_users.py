"""Tests for users.py: /etc/passwd and /etc/group parsing.

TODO:
    - test_parse_passwd_normal() (valid passwd lines → correct user dicts)
    - test_parse_passwd_skips_system_uid() (UID < 1000 excluded)
    - test_parse_passwd_skips_skip_list() (root, daemon, dbus excluded)
    - test_parse_passwd_skips_systemd_prefix() (systemd-timesync etc. excluded)
    - test_parse_group_normal() (valid group lines → correct group dicts)
    - test_parse_group_with_members() (comma-separated members split correctly)
    - test_parse_passwd_malformed() (incomplete lines <7 fields skipped)
"""
