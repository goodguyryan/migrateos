"""Argparse CLI with three subcommands: scan, generate, scan-and-generate.

TODO:
    - Implement build_parser() -> ArgumentParser
    - scan subcommand: --output, --config-path (append), --app-path (append), --include-network, --include-ssh-keys, --include-sudoers, --include-selinux-modules, --dry-run
    - generate subcommand: --manifest, --output
    - scan-and-generate subcommand: same flags as scan + auto-runs generate
    - Implement cmd_scan(args) -> None (orchestrates all 12 scanners, bundler, saves manifest, prints summary)
    - Implement cmd_generate(args) -> None (loads manifest, calls ansible_generator.generate)
    - Implement cmd_scan_and_generate(args) -> None (runs scan then generate)
    - Scanner orchestration order in scan: os_facts, packages, services, users, directories, configs, firewalld, cron, selinux, network, sysctl, containers
    - Print summary with counts, warnings, and "next steps" block
"""
