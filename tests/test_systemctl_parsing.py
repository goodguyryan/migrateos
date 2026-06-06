"""Tests for systemctl output parsing: services.py.

TODO:
    - test_parse_unit_files_normal() (enabled/disabled/static/masked states)
    - test_parse_unit_files_empty()
    - test_parse_running_units()
    - test_parse_running_units_empty()
    - test_classify_service_infrastructure() (postgresql, nginx, redis, mariadb, etc.)
    - test_classify_service_application() (user apps)
    - test_detect_timer_activation_positive()
    - test_detect_timer_activation_negative()
    - test_detect_socket_activation_positive()
    - test_detect_socket_activation_negative()
"""
