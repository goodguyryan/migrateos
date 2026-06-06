"""Scan systemd services: enabled state, running state, custom units, activation type, tier classification.

TODO:
    - _parse_unit_files(text: str) -> dict[str, str] (parse systemctl list-unit-files output: name -> state)
    - _parse_running_units(text: str) -> set[str] (parse systemctl list-units output, extract running service names)
    - _scan_custom_units() -> List[dict] (scan /etc/systemd/system/*.service, skip symlinks to /usr/lib)
    - _parse_environment_file(unit_path: Path) -> List[str] (parse unit file for EnvironmentFile= directives)
    - _detect_timer_activation(name: str) -> bool (check for same-named .timer file)
    - _detect_socket_activation(name: str) -> bool (check for same-named .socket file)
    - _classify_service(name: str) -> str ("infrastructure" for postgresql/nginx/redis etc., "application" for everything else)
    - collect() -> dict (orchestrate: unit files, running units, custom units, classification)
    - Return: [{name, enabled, state, custom_unit, unit_file, environment_files, timer_activated, socket_activated, service_tier}]
"""
