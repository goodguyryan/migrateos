"""Scan NetworkManager connections — detection only, optional review-dir copy.

TODO:
    - _parse_nmcli(text: str) -> List[dict] (parse nmcli -t connection show output)
    - collect(include_network=False) -> dict
    - With --include-network: copy connection files to review/ directory (NOT into Ansible role)
    - Return: {custom_connections, connections, warning}
"""
