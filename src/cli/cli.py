"""CLI entry point for MigrateOS. Argparse setup + subcommand dispatch."""
import argparse
from typing import List
from pathlib import Path
from src.utils.yaml_utils import load_yaml, save_yaml
from src.scanner import (os_facts,
                         packages,
                         services,
                         users,
                         directories,
                         configs,
                         cron,
                         selinux,
                         network,
                         sysctl,
                         containers)
from src.bundler.file_collector import bundle_manifest
from src.generator.ansible_generator import generate

def count_running(services: List[dict]) -> int:
    running = 0
    for service in services:
        if service.get("state") == "running":
            running += 1
    
    return running

def print_summary(manifest: dict, bundle_result: dict, output_dir: str) -> None:
    packages = manifest["packages"]["packages"]
    services = manifest["services"]["services"]
    users = manifest["users"]["users"]
    config_count = len(manifest["configs"]["config_files"])
    running = count_running(services)

    print(f"\n{'='*60}")
    print(f"  MigrateOS Scan Complete")
    print(f"{'='*60}")
    print(f"  Packages:       {len(packages)}")
    print(f"  DNF Groups:     {len(manifest['packages']['groups'])}")
    print(f"  Services:       {len(services)} ({running} running)")
    print(f"  Users:          {len(users)}")
    print(f"  Config files:   {config_count}")
    print(f"  Cron entries:   {len(manifest['cron']['files'])}")
    print(f"  Sysctl files:   {len(manifest['sysctl']['files'])}")
    print(f"  Bundled files:  {len(bundle_result['copied'])}")
    print(f"  Skipped files:  {len(bundle_result['skipped'])}")

    if bundle_result["warnings"]:
        print(f"\n  Warnings:")
        for w in bundle_result["warnings"][:5]:
            print(f"    - {w}")
        if len(bundle_result["warnings"]) > 5:
            remaining = len(bundle_result["warnings"]) - 5
            print(f"    ... and {remaining} more")

    print(f"\n  Next steps:")
    print(f"  1. Review {output_dir / 'manifest.yml'}")
    print(f"  2. Run: python migrate_scan.py generate --manifest {output_dir / 'manifest.yml'} --output {output_dir}")
    print(f"{'='*60}\n")     

def cmd_scan(args):
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    config_paths = [Path(p) for p in args.config_path]
    app_paths = [Path(p) for p in args.app_path]

    manifest = {}

    manifest["os_facts"] = os_facts.collect()
    manifest["packages"] = packages.collect()
    manifest["services"] = services.collect()
    manifest["users"] = users.collect(
        app_paths=[str(p) for p in app_paths],
        config_paths=[str(p) for p in config_paths],
        include_ssh_keys=args.include_ssh_keys,
        include_sudoers=args.include_sudoers,
    )
    manifest["directories"] = directories.collect(app_paths)
    config_files, secrets_required, warnings = configs.collect(config_paths)
    manifest["configs"] = {
        "config_files": config_files,
        "secrets_required": secrets_required,
        "warnings": warnings,
    }
    manifest["cron"] = cron.collect()
    manifest["selinux"] = selinux.collect()
    manifest["network"] = network.collect(include_network=args.include_network)
    manifest["sysctl"] = sysctl.collect()
    manifest["containers"] = containers.collect()

    if not args.dry_run:
        bundle_result = bundle_manifest(
            manifest=manifest,
            output_dir=output_dir,
            include_network=args.include_network,
        )
    else:
        bundle_result = {"copied": [], "skipped": [], "warnings": []}

    save_yaml(manifest, output_dir / "manifest.yml")

    print_summary(manifest, bundle_result, output_dir)

def cmd_generate(args):
    manifest_path = Path(args.manifest)
    output_path = Path(args.output)
    manifest = load_yaml(manifest_path)
    if not manifest:
        print(f"Error: manifest not found or empty: {args.manifest}")
        return
    
    generate(manifest_path, output_path)
    generated_dir = output_path / "generated-ansible"
    print(f"Ansible project generated at {generated_dir}")
    print(f"Next steps: cd {generated_dir} && ansible-galaxy collection install -r requirements.yml && ansible-playbook site.yml --check --diff")

def cmd_scan_and_generate(args):
    cmd_scan(args)
    args.manifest = str(Path(args.output) / "manifest.yml")
    cmd_generate(args)

def build_parser():
    parser = argparse.ArgumentParser(
        prog="migrate-scan",
        description="Scan a Fedora server and generate an idempotent Ansible project to recreate it.",
    )
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Scan the current server and save a manifest")
    scan_parser.add_argument("--output", required=True, help="Output directory for manifest and bundled files")
    scan_parser.add_argument("--config-path", action="append", default=[], help="Config file or directory to include")
    scan_parser.add_argument("--app-path", action="append", default=[], help="App directory to scan for metadata")
    scan_parser.add_argument("--include-network", action="store_true", help="Include network connections in manifest")
    scan_parser.add_argument("--include-ssh-keys", action="store_true", help="Include SSH authorized_keys")
    scan_parser.add_argument("--include-sudoers", action="store_true", help="Include sudoers config")
    scan_parser.add_argument("--dry-run", action="store_true", help="Assemble manifest only, skip file bundling")
    scan_parser.set_defaults(func=cmd_scan)

    gen_parser = subparsers.add_parser("generate", help="Generate Ansible project from a manifest")
    gen_parser.add_argument("--manifest", required=True, help="Path to manifest.yml")
    gen_parser.add_argument("--output", required=True, help="Output directory for the Ansible project")
    gen_parser.set_defaults(func=cmd_generate)

    sag_parser = subparsers.add_parser("scan-and-generate", help="Scan server then generate Ansible project")
    sag_parser.add_argument("--output", required=True, help="Output directory for manifest, bundled files, and Ansible project")
    sag_parser.add_argument("--config-path", action="append", default=[], help="Config file or directory to include")
    sag_parser.add_argument("--app-path", action="append", default=[], help="App directory to scan for metadata")
    sag_parser.add_argument("--include-network", action="store_true", help="Include network connections in manifest")
    sag_parser.add_argument("--include-ssh-keys", action="store_true", help="Include SSH authorized_keys")
    sag_parser.add_argument("--include-sudoers", action="store_true", help="Include sudoers config")
    sag_parser.add_argument("--dry-run", action="store_true", help="Assemble manifest only, skip file bundling")
    sag_parser.set_defaults(func=cmd_scan_and_generate)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
