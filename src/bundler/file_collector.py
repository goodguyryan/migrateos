"""Collect and copy files from source server into output directory with safety checks.

TODO:
    - Implement collect_file(src: Path, dest_dir: Path) -> Tuple[bool, str] (uses shutil.copy2, returns success+reason)
    - Implement collect_directory(src_dir: Path, dest_dir: Path) -> Tuple[List[Path], List[str], List[str]]
      (recursive walk, applies is_blocked() + is_excluded() + detect_secrets() to every file)
    - Create destination subdirectories as needed
    - Skip blocked/excluded files, flag secrets
    - Return: (copied_paths, warnings, skipped_secrets)
"""
