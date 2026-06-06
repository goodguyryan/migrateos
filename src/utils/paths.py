"""Path safety checks: blocklist, exclusions, secret detection, runtime detection, include scanning.

TODO:
    - Implement is_blocked(path: Path) -> bool (exact paths: /etc/shadow, prefixes: /etc/ssh/ssh_host_, /var/log/, etc.)
    - Normalize Path to forward-slash strings before blocklist comparison (Windows backslash fix)
    - Implement is_excluded(filename: str) -> bool (*.swp, __pycache__, *.log, etc.)
    - Implement Tier 1 secret detection: detect_secret_filename(name: str) -> bool (.env, id_rsa, *.pem, etc.)
    - Implement Tier 2 secret detection: detect_secrets_in_content(text: str) -> List[str] (regex for PASSWORD=, SECRET=, etc.)
      CRITICAL: use '|'.join(keys) not .format() for regex to avoid {4,} clash
    - Implement detect_runtime(dir: Path) -> Optional[str] (package.json -> node, pyproject.toml -> python, etc.)
    - Implement scan_includes(content: str) -> List[str] (regex for include, Include, IncludeOptional, #includedir, $IncludeConfig, .include)
    - Implement suggest_install(runtime: str) -> List[str] (return suggested install commands per runtime)
"""
