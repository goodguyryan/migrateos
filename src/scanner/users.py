"""Scan local users and groups from /etc/passwd and /etc/group.

TODO:
    - _parse_passwd(text: str) -> List[dict] (parse colon-delimited format: name, uid, gid, home, shell)
    - _parse_group(text: str) -> List[dict] (parse colon-delimited format: name, gid, members)
    - _load_authorized_keys(user_home: str) -> Optional[str] (read ~/.ssh/authorized_keys if --include-ssh-keys)
    - _load_sudoers(username: str) -> Optional[str] (read /etc/sudoers.d/<user> if --include-sudoers)
    - collect(app_paths: List[str], config_paths: List[str], include_ssh_keys=False, include_sudoers=False) -> dict
    - Only include users with UID >= 1000, not in skip list (root, daemon, dbus, systemd-*, etc.)
    - Only migrate users who own at least one --app-path or --config-path
    - DO NOT preserve UID/GID — let Ansible auto-assign
    - Return: {groups: [...], users: [{name, uid, group, groups, home, shell, authorized_keys?, sudoers?}]}
"""
