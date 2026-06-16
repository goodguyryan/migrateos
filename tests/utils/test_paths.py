"""Tests for paths.py: blocklist, exclusions, secret detection, runtime detection, include scanning."""

from pathlib import Path
from src.utils.paths import (is_blocked_path, is_excluded_file,
                             is_secret_file, detect_secrets_in_file,
                             detect_runtime, suggest_install,
                             detect_includes)

def test_is_blocked_exact_match():
    assert is_blocked_path(Path("/etc/shadow")) is True
    assert is_blocked_path(Path("/etc/machine-id")) is True
    assert is_blocked_path(Path("/etc/hostname")) is True


def test_is_blocked_prefix_match():
    assert is_blocked_path(Path("/etc/ssh/ssh_host_rsa_key")) is True
    assert is_blocked_path(Path("/var/log/messages")) is True
    assert is_blocked_path(Path("/proc/cpuinfo")) is True


def test_is_blocked_not_blocked():
    assert is_blocked_path(Path("/etc/nginx/nginx.conf")) is False
    assert is_blocked_path(Path("/home/user/.bashrc")) is False


def test_is_blocked_windows_backslash():
    assert is_blocked_path(Path("\\etc\\shadow")) is True
    assert is_blocked_path(Path("\\etc\\ssh\\ssh_host_rsa_key")) is True

def test_is_excluded_match():
    assert is_excluded_file(".git") is True
    assert is_excluded_file("__pycache__") is True
    assert is_excluded_file("foo.log") is True
    assert is_excluded_file("file.swp") is True
    assert is_excluded_file("node_modules") is True


def test_is_excluded_no_match():
    assert is_excluded_file("nginx.conf") is False
    assert is_excluded_file("myfile.txt") is False
    assert is_excluded_file("important.yaml") is False

def test_is_secret_file_match():
    assert is_secret_file(".env") is True
    assert is_secret_file("id_rsa") is True
    assert is_secret_file("secret.key") is True
    assert is_secret_file("server.pem") is True
    assert is_secret_file("api_token.txt") is True


def test_is_secret_file_no_match():
    assert is_secret_file("id_rsa.pub") is False
    assert is_secret_file("nginx.conf") is False
    assert is_secret_file("README.md") is False


def test_is_secret_in_file_match():
    results = detect_secrets_in_file("PASSWORD=abc12345")
    assert len(results) == 1
    assert "PASSWORD=abc12345" in results

    results = detect_secrets_in_file("API_KEY: my-secret-token")
    assert len(results) == 1
    assert "API_KEY" in results[0]


def test_is_secret_in_file_no_match():
    assert detect_secrets_in_file("just regular text") == []
    assert detect_secrets_in_file("PASSWORD=") == []  # value too short


def test_is_secret_in_file_no_regex_crash():
    text = "DATABASE_URL=postgres://user:pass@localhost/db"
    results = detect_secrets_in_file(text)
    assert len(results) == 1
    assert "DATABASE_URL" in results[0]


def test_detect_runtime_node(temp_dir):
    (temp_dir / "package.json").write_text("{}")
    assert detect_runtime(temp_dir) == "node"


def test_detect_runtime_python_requirements(temp_dir):
    (temp_dir / "requirements.txt").write_text("flask")
    assert detect_runtime(temp_dir) == "python"


def test_detect_runtime_python_pyproject(temp_dir):
    (temp_dir / "pyproject.toml").write_text("[tool]")
    assert detect_runtime(temp_dir) == "python"


def test_detect_runtime_python_setup(temp_dir):
    (temp_dir / "setup.py").write_text("from setuptools import setup")
    assert detect_runtime(temp_dir) == "python"


def test_detect_runtime_java_maven(temp_dir):
    (temp_dir / "pom.xml").write_text("<project></project>")
    assert detect_runtime(temp_dir) == "java"


def test_detect_runtime_java_gradle(temp_dir):
    (temp_dir / "build.gradle").write_text("plugins {}")
    assert detect_runtime(temp_dir) == "java"


def test_detect_runtime_go(temp_dir):
    (temp_dir / "go.mod").write_text("module example")
    assert detect_runtime(temp_dir) == "go"


def test_detect_runtime_rust(temp_dir):
    (temp_dir / "Cargo.toml").write_text("[package]")
    assert detect_runtime(temp_dir) == "rust"


def test_detect_runtime_ruby(temp_dir):
    (temp_dir / "Gemfile").write_text("source 'https://rubygems.org'")
    assert detect_runtime(temp_dir) == "ruby"


def test_detect_runtime_php(temp_dir):
    (temp_dir / "composer.json").write_text("{}")
    assert detect_runtime(temp_dir) == "php"


def test_detect_runtime_none(temp_dir):
    assert detect_runtime(temp_dir) is None


def test_detect_runtime_multiple(temp_dir):
    (temp_dir / "package.json").write_text("{}")
    (temp_dir / "pyproject.toml").write_text("[tool]")
    assert detect_runtime(temp_dir) == "multiple"


def test_suggest_install_returns_commands():
    cmds = suggest_install("python")
    assert len(cmds) > 0
    assert any("pip" in c for c in cmds)

    cmds = suggest_install("node")
    assert any("npm" in c for c in cmds)

    cmds = suggest_install("unknown_runtime")
    assert cmds == []


def test_detect_includes_nginx():
    content = "include /etc/nginx/conf.d/*.conf;"
    assert detect_includes(content) == ["/etc/nginx/conf.d/*.conf"]


def test_detect_includes_apache():
    content = "Include /etc/httpd/conf.d/ssl.conf"
    assert detect_includes(content) == ["/etc/httpd/conf.d/ssl.conf"]


def test_detect_includes_sshd():
    content = "Include /etc/ssh/sshd_config.d/*.conf"
    assert detect_includes(content) == ["/etc/ssh/sshd_config.d/*.conf"]


def test_detect_includes_sudoers():
    content = "#includedir /etc/sudoers.d"
    assert detect_includes(content) == ["/etc/sudoers.d"]


def test_detect_includes_syslog():
    content = "$IncludeConfig /etc/rsyslog.d/*.conf"
    assert detect_includes(content) == ["/etc/rsyslog.d/*.conf"]


def test_detect_includes_systemd():
    content = ".include /usr/lib/systemd/system/httpd.service"
    assert detect_includes(content) == ["/usr/lib/systemd/system/httpd.service"]


def test_detect_includes_none():
    content = "# this is just a comment\nserver_name example.com;"
    assert detect_includes(content) == []


def test_detect_includes_no_false_positives():
    content = "Here is a text that doesn't #include anything special"
    assert detect_includes(content) == []