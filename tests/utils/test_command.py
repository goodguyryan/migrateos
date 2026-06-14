"""Tests for command.py: safe_run and force_run subprocess wrappers."""

import subprocess
import sys

import pytest

from src.utils.command import force_run, safe_run


def test_safe_run_success():
    success, stdout, stderr = safe_run(
        [sys.executable, "-c", "print('hello')"]
    )
    assert success is True
    assert stdout.strip() == "hello"
    assert stderr == ""


def test_safe_run_nonzero_exit():
    success, stdout, stderr = safe_run(
        [sys.executable, "-c", "import sys; sys.exit(1)"]
    )
    assert success is False
    assert stdout == ""


def test_safe_run_stderr_captured():
    success, stdout, stderr = safe_run(
        [sys.executable, "-c", "import sys; print('bad', file=sys.stderr); sys.exit(2)"]
    )
    assert success is False
    assert "bad" in stderr


def test_safe_run_missing_command():
    success, stdout, stderr = safe_run(["nonexistent_binary_xyz123"])
    assert success is False
    assert stdout == ""
    assert len(stderr) > 0


def test_force_run_returns_stripped_stdout():
    output = force_run(
        [sys.executable, "-c", "print('  hello  ')"]
    )
    assert output == "hello"


def test_force_run_raises_on_nonzero():
    with pytest.raises(subprocess.CalledProcessError):
        force_run([sys.executable, "-c", "import sys; sys.exit(1)"])


def test_force_run_raises_on_missing():
    with pytest.raises(FileNotFoundError):
        force_run(["nonexistent_binary_xyz123"])
