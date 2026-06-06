"""YAML read/write helpers with consistent defaults.

TODO:
    - Implement load_yaml(path: Path) -> dict (returns {} on missing/unreadable file)
    - Implement save_yaml(data: dict, path: Path) -> None (creates parent dirs, block style, sorted keys, no anchors/tags)
    - Handle PermissionError, IsADirectoryError gracefully
"""
