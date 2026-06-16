"""Tests for containers.py: Docker/Podman container detection.

TODO:
    - test_parse_docker_ps_output() (docker ps output → container names parsed)
    - test_parse_podman_ps_output() (podman ps output → container names parsed)
    - test_collect_with_no_containers() (empty output → empty runtimes, no warning)
"""
