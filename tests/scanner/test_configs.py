"""Tests for configs.py: config file/directory metadata collection with safety checks.

TODO:
    - test_collect_file_basic() (stat, sha256, preview populated)
    - test_collect_file_secret_detection() (content with PASSWORD= → secrets detected)
    - test_collect_file_include_detection() (content with Include directive → includes detected)
    - test_collect_directory_small() (≤30 files → copy_method "single")
    - test_collect_directory_large() (>30 files → copy_method "directory")
    - test_collect_directory_blocked() (blocked files skipped)
    - test_collect_directory_excluded() (*.swp files skipped)
    - test_collect_symlink() (symlink detected, target resolved)
    - test_collect_missing_path() (nonexistent → warning, not in results)
"""
