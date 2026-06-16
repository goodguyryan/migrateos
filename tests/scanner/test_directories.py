"""Tests for directories.py: app directory metadata and runtime detection.

TODO:
    - test_collect_existing_directory() (temp_dir with package.json → runtime detected as node)
    - test_collect_missing_directory() (nonexistent path → warning entry)
    - test_collect_empty_directory() (dir with no runtime markers → detected_runtime is None)
"""
