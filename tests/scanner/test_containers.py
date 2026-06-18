"""Tests for containers.py: Docker/Podman container detection."""

from src.scanner.containers import parse_docker_ps, parse_podman_ps

def test_parse_docker_ps_normal():
    text = """\
web-app
db
cache
"""
    result = parse_docker_ps(text)
    assert result == ["web-app", "db", "cache"]

def test_parse_docker_ps_empty():
    result = parse_docker_ps("")
    assert result == []

def test_parse_podman_ps_normal():
    text = """\
my-nginx
my-postgres
"""
    result = parse_podman_ps(text)
    assert result == ["my-nginx", "my-postgres"]

def test_parse_podman_ps_empty():
    result = parse_podman_ps("")
    assert result == []