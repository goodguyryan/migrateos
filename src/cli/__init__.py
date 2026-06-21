"""CLI entry point for MigrateOS. Argparse setup + subcommand dispatch."""

from src.cli.cli import build_parser, cmd_scan, cmd_generate, cmd_scan_and_generate, main