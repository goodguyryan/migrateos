"""Tests for services.py: systemd service scanning (unit files, running units, classification).

TODO:
    - test_parse_unit_files_normal() (enabled/disabled/static/masked states)
    - test_parse_unit_files_empty()
    - test_parse_running_units() (running service names extracted)
    - test_parse_running_units_empty()
    - test_classify_service_infrastructure() (postgresql, nginx, redis, mariadb, etc.)
    - test_classify_service_application() (user apps)
    - test_detect_timer_activation_positive()
    - test_detect_timer_activation_negative()
    - test_detect_socket_activation_positive()
    - test_detect_socket_activation_negative()
    - test_parse_environment_file() (unit file with EnvironmentFile= directives)
"""
