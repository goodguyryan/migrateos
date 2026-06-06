"""Tests for paths.py: blocklist, exclusions, Tier 1/Tier 2 secret detection.

TODO:
    - test_is_blocked_exact_match() (e.g., /etc/shadow, /etc/machine-id)
    - test_is_blocked_prefix_match() (e.g., /etc/ssh/ssh_host_rsa_key)
    - test_is_blocked_not_blocked() (normal config files)
    - test_is_blocked_windows_backslash_normalization()
    - test_is_excluded_match() (__pycache__, *.log, .git, etc.)
    - test_is_excluded_no_match()
    - test_detect_secret_filename_tier1_match() (.env, id_rsa, *.pem, etc.)
    - test_detect_secret_filename_tier1_no_match()
    - test_detect_secrets_in_content_tier2_match() (PASSWORD=, SECRET=, API_KEY=, etc.)
    - test_detect_secrets_in_content_tier2_no_match()
    - test_detect_secrets_in_content_no_format_placeholder_bug() (verify {4,} doesn't crash)
"""
