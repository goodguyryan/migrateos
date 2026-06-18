"""Tests for services.py: systemd service scanning."""

from src.scanner.services import (
    parse_unit_files,
    parse_running_units,
    classify_service,
    detect_timer_activation,
    detect_socket_activation,
    parse_environment_file,
)

def test_parse_unit_files_normal():
    text = """\
sshd.service                               enabled
nginx.service                              disabled
myapp.service                              static
some-service.service                       masked
"""
    result = parse_unit_files(text)
    assert result == {
        "sshd.service": "enabled",
        "nginx.service": "disabled",
        "myapp.service": "static",
        "some-service.service": "masked",
    }

def test_parse_unit_files_empty():
    assert parse_unit_files("") == {}

def test_parse_running_units():
    text = """\
sshd.service     loaded active running OpenSSH server daemon
nginx.service    loaded active running nginx web server
"""
    result = parse_running_units(text)
    assert result == {"sshd.service", "nginx.service"}

def test_parse_running_units_empty():
    assert parse_running_units("") == set()

def test_classify_service_infrastructure():
    assert classify_service("postgresql.service") == "infrastructure"
    assert classify_service("nginx.service") == "infrastructure"
    assert classify_service("redis.service") == "infrastructure"
    assert classify_service("mariadb.service") == "infrastructure"
    assert classify_service("sshd.service") == "infrastructure"
    assert classify_service("docker.service") == "infrastructure"
    assert classify_service("haproxy.service") == "infrastructure"

def test_classify_service_application():
    assert classify_service("myapp.service") == "application"
    assert classify_service("gunicorn.service") == "application"
    assert classify_service("myapp@.service") == "application"

def test_detect_timer_activation_positive(temp_dir):
    (temp_dir / "myapp.timer").write_text("[Timer]\n")
    assert detect_timer_activation("myapp", temp_dir) is True

def test_detect_timer_activation_negative(temp_dir):
    assert detect_timer_activation("myapp", temp_dir) is False

def test_detect_socket_activation_positive(temp_dir):
    (temp_dir / "myapp.socket").write_text("[Socket]\n")
    assert detect_socket_activation("myapp", temp_dir) is True

def test_detect_socket_activation_negative(temp_dir):
    assert detect_socket_activation("myapp", temp_dir) is False

def test_parse_environment_file(temp_dir):
    unit = temp_dir / "myapp.service"
    unit.write_text("""\
[Service]
EnvironmentFile=/etc/myapp/env.conf
EnvironmentFile=-/etc/myapp/optional.conf
ExecStart=/usr/bin/myapp
""")
    result = parse_environment_file(unit)
    assert result == ["/etc/myapp/env.conf", "/etc/myapp/optional.conf"]
