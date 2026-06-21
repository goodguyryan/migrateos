"""Tests for src.cli: argparse setup and subcommand dispatch."""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.scanner import users, configs
from src.cli.cli import (build_parser, 
                     cmd_scan, 
                     cmd_generate, 
                     cmd_scan_and_generate,
                     main)

def test_scan_subcommand_exists():
    parser = build_parser()
    args = parser.parse_args(["scan", "--output", "/tmp"])
    assert args.command == "scan"
    assert args.func is cmd_scan

def test_scan_required_output_flag():
    parser = build_parser()
    args = parser.parse_args(["scan", "--output", "/tmp/mydir"])
    assert args.output == "/tmp/mydir"

def test_scan_config_path_append():
    parser = build_parser()
    args = parser.parse_args([
        "scan", "--output", "/tmp",
        "--config-path", "/etc/nginx",
        "--config-path", "/etc/redis",
    ])
    assert args.config_path == ["/etc/nginx", "/etc/redis"]

def test_scan_app_path_append():
    parser = build_parser()
    args = parser.parse_args([
        "scan", "--output", "/tmp",
        "--app-path", "/var/www",
        "--app-path", "/srv/api",
    ])
    assert args.app_path == ["/var/www", "/srv/api"]

def test_scan_boolean_flags_default_false():
    parser = build_parser()
    args = parser.parse_args(["scan", "--output", "/tmp"])
    assert args.include_network is False
    assert args.include_ssh_keys is False
    assert args.include_sudoers is False
    assert args.dry_run is False

def test_scan_boolean_flags_set_true():
    parser = build_parser()
    args = parser.parse_args([
        "scan", "--output", "/tmp",
        "--include-network",
        "--include-ssh-keys",
        "--include-sudoers",
        "--dry-run",
    ])
    assert args.include_network is True
    assert args.include_ssh_keys is True
    assert args.include_sudoers is True
    assert args.dry_run is True

def test_generate_subcommand_exists():
    parser = build_parser()
    args = parser.parse_args(["generate", "--manifest", "manifest.yml", "--output", "/tmp"])
    assert args.command == "generate"
    assert args.func is cmd_generate

def test_generate_required_flags():
    parser = build_parser()
    args = parser.parse_args(["generate", "--manifest", "path/to/manifest.yml", "--output", "path/to/output"])
    assert args.manifest == "path/to/manifest.yml"
    assert args.output == "path/to/output"

def test_scan_and_generate_has_same_flags_as_scan():
    parser = build_parser()
    args = parser.parse_args([
        "scan-and-generate", "--output", "/tmp",
        "--config-path", "/etc/nginx",
        "--app-path", "/var/www",
        "--include-network",
        "--include-ssh-keys",
        "--include-sudoers",
        "--dry-run",
    ])
    assert args.command == "scan-and-generate"
    assert args.output == "/tmp"
    assert args.config_path == ["/etc/nginx"]
    assert args.app_path == ["/var/www"]
    assert args.include_network is True
    assert args.include_ssh_keys is True
    assert args.include_sudoers is True
    assert args.dry_run is True
    assert args.func is cmd_scan_and_generate

def test_invalid_subcommand_exits():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["foobar"])

def test_generate_calls_generator():
    mock_args = MagicMock()
    mock_args.manifest = "/path/to/manifest.yml"
    mock_args.output = "/path/to/output"
    with patch("src.cli.cli.generate") as mock_generate:
        with patch("src.cli.cli.load_yaml", return_value={"os_facts": {}}):
            cmd_generate(mock_args)
    mock_generate.assert_called_once()
    call_args = mock_generate.call_args[0]
    assert call_args[0] == Path(mock_args.manifest)
    assert call_args[1] == Path(mock_args.output)

def test_generate_prints_success_message(capsys):
    mock_args = MagicMock()
    mock_args.manifest = "/path/to/manifest.yml"
    mock_args.output = "/path/to/output"
    with patch("src.cli.cli.generate"):
        with patch("src.cli.cli.load_yaml", return_value={"os_facts": {}}):
            cmd_generate(mock_args)
    captured = capsys.readouterr()
    assert "Ansible project generated at" in captured.out
    assert "generated-ansible" in captured.out

def test_generate_manifest_not_found(capsys):
    mock_args = MagicMock()
    mock_args.manifest = "/nonexistent/manifest.yml"
    mock_args.output = "/path/to/output"
    with patch("src.cli.cli.generate") as mock_generate:
        with patch("src.cli.cli.load_yaml", return_value={}):
            cmd_generate(mock_args)
    mock_generate.assert_not_called()
    captured = capsys.readouterr()
    assert "Error" in captured.out

def test_generate_receives_path_objects():
    mock_args = MagicMock()
    mock_args.manifest = "/path/to/manifest.yml"
    mock_args.output = "/path/to/output"
    with patch("src.cli.cli.generate") as mock_generate:
        with patch("src.cli.cli.load_yaml", return_value={"os_facts": {}}):
            cmd_generate(mock_args)
    call_args = mock_generate.call_args[0]
    assert isinstance(call_args[0], Path)
    assert isinstance(call_args[1], Path)

def test_scan_assembles_manifest_keys(mock_scanners, temp_dir):
    from unittest.mock import patch
    from src.cli.cli import cmd_scan
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    saved_data = {}
    with patch("src.cli.cli.save_yaml") as mock_save:
        mock_save.side_effect = lambda data, path: saved_data.update(data)
        cmd_scan(mock_args)
    expected_keys = {"os_facts", "packages", "services", "users", "directories",
                     "configs", "cron", "selinux", "network", "sysctl", "containers"}
    assert expected_keys.issubset(set(saved_data.keys()))

def test_scan_configs_repacked_correctly(mock_scanners, temp_dir):
    from unittest.mock import patch
    from src.cli.cli import cmd_scan
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    saved_data = {}
    with patch("src.cli.cli.save_yaml") as mock_save:
        mock_save.side_effect = lambda data, path: saved_data.update(data)
        cmd_scan(mock_args)
    configs = saved_data["configs"]
    assert isinstance(configs, dict)
    assert "config_files" in configs
    assert "secrets_required" in configs
    assert "warnings" in configs
    assert isinstance(configs["config_files"], list)
    assert isinstance(configs["secrets_required"], list)
    assert isinstance(configs["warnings"], list)

def test_scan_directories_stored_as_list(mock_scanners, temp_dir):
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    saved_data = {}
    with patch("src.cli.cli.save_yaml") as mock_save:
        mock_save.side_effect = lambda data, path: saved_data.update(data)
        cmd_scan(mock_args)
    directories = saved_data["directories"]
    assert isinstance(directories, list)
    assert len(directories) > 0

def test_scan_users_receives_correct_flags(mock_scanners):
    mock_args = MagicMock()
    mock_args.output = "/tmp/test"
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = True
    mock_args.include_sudoers = True
    mock_args.include_network = False
    mock_args.dry_run = False
    with patch("src.cli.cli.save_yaml"):
        cmd_scan(mock_args)
    call_kwargs = users.collect.call_args.kwargs if users.collect.call_args else {}
    assert call_kwargs.get("include_ssh_keys") is True
    assert call_kwargs.get("include_sudoers") is True

def test_scan_saves_manifest_to_output(mock_scanners, temp_dir):
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    with patch("src.cli.cli.save_yaml") as mock_save:
        cmd_scan(mock_args)
    mock_save.assert_called_once()
    saved_path = mock_save.call_args[0][1]
    assert saved_path == temp_dir / "manifest.yml"

def test_scan_empty_config_paths(mock_scanners):
    mock_args = MagicMock()
    mock_args.output = "/tmp/test"
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    with patch("src.cli.cli.save_yaml"):
        cmd_scan(mock_args)
    call_args = configs.collect.call_args[0][0]
    assert call_args == []

def test_scan_calls_bundler_when_not_dry_run(mock_scanners, temp_dir):
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    controlled_result = {"copied": ["file1.conf"], "skipped": ["secret.key"], "warnings": []}
    with patch("src.cli.cli.save_yaml"):
        with patch("src.cli.cli.bundle_manifest", return_value=controlled_result) as mock_bundle:
            cmd_scan(mock_args)
    mock_bundle.assert_called_once()
    call_kwargs = mock_bundle.call_args.kwargs
    assert "manifest" in call_kwargs
    assert "output_dir" in call_kwargs
    assert "include_network" in call_kwargs
    assert call_kwargs["output_dir"] == temp_dir
    assert call_kwargs["include_network"] is False

def test_scan_skips_bundler_when_dry_run(mock_scanners, temp_dir):
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = True
    with patch("src.cli.cli.save_yaml"):
        with patch("src.cli.cli.bundle_manifest") as mock_bundle:
            cmd_scan(mock_args)
    mock_bundle.assert_not_called()

def test_scan_summary_shows_package_count(mock_scanners, temp_dir, capsys):
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    controlled_result = {"copied": [], "skipped": [], "warnings": []}
    with patch("src.cli.cli.save_yaml"):
        with patch("src.cli.cli.bundle_manifest", return_value=controlled_result):
            cmd_scan(mock_args)
    captured = capsys.readouterr()
    assert "Packages:" in captured.out

def test_scan_summary_shows_warnings(mock_scanners, temp_dir, capsys):
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    controlled_result = {"copied": [], "skipped": [], "warnings": ["Test warning: something went wrong"]}
    with patch("src.cli.cli.save_yaml"):
        with patch("src.cli.cli.bundle_manifest", return_value=controlled_result):
            cmd_scan(mock_args)
    captured = capsys.readouterr()
    assert "Warnings:" in captured.out
    assert "Test warning: something went wrong" in captured.out

def test_scan_summary_shows_next_steps(mock_scanners, temp_dir, capsys):
    mock_args = MagicMock()
    mock_args.output = str(temp_dir)
    mock_args.config_path = []
    mock_args.app_path = []
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = False
    controlled_result = {"copied": [], "skipped": [], "warnings": []}
    with patch("src.cli.cli.save_yaml"):
        with patch("src.cli.cli.bundle_manifest", return_value=controlled_result):
            cmd_scan(mock_args)
    captured = capsys.readouterr()
    assert "Next steps:" in captured.out
    assert "manifest.yml" in captured.out

def test_scan_and_generate_calls_both():
    mock_args = MagicMock()
    with patch("src.cli.cli.cmd_scan") as mock_scan:
        with patch("src.cli.cli.cmd_generate") as mock_generate:
            cmd_scan_and_generate(mock_args)
    mock_scan.assert_called_once_with(mock_args)
    mock_generate.assert_called_once_with(mock_args)

def test_scan_and_generate_uses_same_output_dir():
    mock_args = MagicMock()
    mock_args.output = "/path/to/output"
    with patch("src.cli.cli.cmd_scan"):
        with patch("src.cli.cli.cmd_generate"):
            cmd_scan_and_generate(mock_args)
    assert Path(mock_args.manifest) == Path("/path/to/output") / "manifest.yml"

def test_scan_and_generate_skips_generate_on_scan_failure():
    mock_args = MagicMock()
    with patch("src.cli.cli.cmd_scan", side_effect=RuntimeError("scan failed")):
        with patch("src.cli.cli.cmd_generate") as mock_generate:
            with pytest.raises(RuntimeError):
                cmd_scan_and_generate(mock_args)
    mock_generate.assert_not_called()

def test_main_dispatches_scan_to_cmd_scan():
    with patch("sys.argv", ["migrate-scan", "scan", "--output", "/tmp"]):
        with patch("src.cli.cli.cmd_scan") as mock_scan:
            main()
    mock_scan.assert_called_once()

def test_main_dispatches_generate_to_cmd_generate():
    with patch("sys.argv", ["migrate-scan", "generate", "--manifest", "m.yml", "--output", "/tmp"]):
        with patch("src.cli.cli.cmd_generate") as mock_generate:
            main()
    mock_generate.assert_called_once()

def test_main_no_subcommand_prints_help(capsys):
    with patch("sys.argv", ["migrate-scan"]):
        main()
    captured = capsys.readouterr()
    assert "usage:" in captured.out

def test_entry_point_does_not_crash_on_import():
    import migrate_scan
    assert hasattr(migrate_scan, "main")

def test_full_scan_generate_pipeline(mock_scanners, temp_dir):
    import yaml
    from pathlib import Path
    from unittest.mock import MagicMock
    from src.cli.cli import cmd_scan, cmd_generate

    output_dir = temp_dir / "scan_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    mock_args = MagicMock()
    mock_args.output = str(output_dir)
    mock_args.config_path = ["/fake/config"]
    mock_args.app_path = ["/fake/app"]
    mock_args.include_ssh_keys = False
    mock_args.include_sudoers = False
    mock_args.include_network = False
    mock_args.dry_run = True

    cmd_scan(mock_args)

    manifest_path = output_dir / "manifest.yml"
    assert manifest_path.exists()

    with manifest_path.open("r", encoding="utf-8") as f:
        saved_manifest = yaml.safe_load(f)

    expected_keys = {"os_facts", "packages", "services", "users", "directories",
                     "configs", "cron", "selinux", "network", "sysctl", "containers"}
    assert expected_keys.issubset(set(saved_manifest.keys()))

    mock_args = MagicMock()
    mock_args.manifest = str(manifest_path)
    mock_args.output = str(output_dir)

    cmd_generate(mock_args)

    ansible_dir = output_dir / "generated-ansible"
    assert ansible_dir.is_dir()
    assert (ansible_dir / "ansible.cfg").is_file()
    assert (ansible_dir / "inventory.ini").is_file()
    assert (ansible_dir / "site.yml").is_file()
    assert (ansible_dir / "WARNINGS.md").is_file()
    assert (ansible_dir / "group_vars").is_dir()
    assert (ansible_dir / "roles" / "migrated_server" / "tasks").is_dir()

    inventory_content = (ansible_dir / "inventory.ini").read_text(encoding="utf-8")
    assert "CHANGE_ME" in inventory_content
