"""YAML read/write helpers with consistent defaults."""
import yaml
from pathlib import Path
from typing import Any, Dict


def load_yaml(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        return {}
    
def save_yaml(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            sort_keys=True,
            allow_unicode=True,
            Dumper=yaml.SafeDumper
        )
