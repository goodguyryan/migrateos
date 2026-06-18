"""Detect running Docker and Podman containers — warning only, no auto-migration."""

from typing import List
from src.utils.command import safe_run

def parse_docker_ps(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]

def parse_podman_ps(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]

def collect() -> dict:
    runtimes = []
    containers = []

    ok, docker_out, _ = safe_run(["docker", "ps", "--format", "{{.Names}}"])
    if ok and docker_out.strip():
        runtimes.append("docker")
        containers.extend(parse_docker_ps(docker_out))

    ok, podman_out, _ = safe_run(["podman", "ps", "--format", "{{.Names}}"])
    if ok and podman_out.strip():
        runtimes.append("podman")
        containers.extend(parse_podman_ps(podman_out))

    warning = None
    if containers:
        warning = (
            f"Running containers detected: {', '.join(containers)}. "
            "Container state cannot be auto-migrated. "
            "Use docker commit/podman commit manually."
        )

    return {
        "runtimes": runtimes,
        "running_containers": containers,
        "warning": warning,
    }
