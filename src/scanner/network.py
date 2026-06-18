"""Scan NetworkManager connections — detection only, optional review-dir copy."""

from typing import List
from src.utils.command import safe_run

def parse_nmcli(text: str) -> List[dict]:
    """Parse nmcli -t connection show terse output.
    Format: NAME:UUID:TYPE:DEVICE
    """
    connections = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(":")
        if len(parts) >= 4:
            connections.append({
                "name": parts[0],
                "uuid": parts[1],
                "type": parts[2],
                "device": parts[3],
            })
    return connections

def collect(include_network: bool = False) -> dict:
    """Detect NetworkManager connections. Warn unless --include-network is set."""
    _, nmcli_out, _ = safe_run(["nmcli", "-t", "connection", "show"])
    connections = parse_nmcli(nmcli_out)

    warning = None
    if include_network:
        warning = (
            "Network connections included in review/ directory. "
            "Review carefully — network config is server-specific."
        )
    elif connections:
        warning = (
            "Network connections detected but not included. "
            "Use --include-network to copy to review/ directory."
        )

    return {
        "connections": connections,
        "custom_connections": connections,
        "warning": warning,
    }
