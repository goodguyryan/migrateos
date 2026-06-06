"""Scan config files and directories with safety checks and copy method decisions.

TODO:
    - _collect_file(config_path: Path) -> dict (stat, sha256, preview 200 lines, secret check, include scan)
    - _collect_directory(config_path: Path) -> dict (recursive walk, apply is_blocked + is_excluded per file)
    - collect(config_paths: List[Path]) -> Tuple[List[dict], List[str], List[str]]
    - Symlinks: follow target, warn
    - Threshold: <=30 files -> copy_method "single"; >30 -> copy_method "directory"
    - Return: (config_files, secrets_required, warnings)
"""
