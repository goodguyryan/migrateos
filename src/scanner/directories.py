"""Scan app directories for metadata: ownership, mode, runtime detection, install suggestions.

TODO:
    - collect(app_paths: List[Path]) -> List[dict]
    - For each path: stat owner/group/mode, call detect_runtime(), call suggest_install()
    - Does NOT copy files — bundler handles that
    - Return: [{name, path, bundled_src, owner, group, mode, detected_runtime, suggested_install_commands}]
"""
