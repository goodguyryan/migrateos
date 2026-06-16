"""Tests for cron.py: cron files and systemd timer scanning.

TODO:
    - test_scan_cron_dirs_with_files() (temp_dir with cron scripts → files found)
    - test_scan_cron_dirs_empty_dirs() (empty directories → empty list)
    - test_scan_systemd_timers() (temp_dir with .timer files → timers detected)
"""
