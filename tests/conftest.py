"""Shared pytest fixtures for the MigrateOS test suite.

TODO:
    - Fixture sample_manifest() -> dict (complete minimal manifest exercising all sections: os, packages, services, users, configs, firewalld, cron, sysctl, secrets, warnings, databases, containers, network)
    - Fixture temp_dir() -> Path (creates temporary directory, yields it, cleans up after test)
"""
