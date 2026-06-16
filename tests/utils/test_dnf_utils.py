"""Tests for dnf_version.py: DNF4 vs DNF5 command construction."""

from src.utils.dnf_utils import return_userinstalled_cmd, return_group_list_cmd

def test_userinstalled_cmd_dnf4():
    assert return_userinstalled_cmd("dnf") == \
        ["dnf", "repoquery", "--userinstalled", "--qf", "%{name}"]


def test_userinstalled_cmd_dnf5():
    assert return_userinstalled_cmd("dnf5") == \
        ["dnf5", "repoquery", "--userinstalled", "--qf", "%{name}"]


def test_group_list_cmd_dnf4():
    assert return_group_list_cmd("dnf") == ["dnf", "group", "list", "--installed", "--ids"]


def test_group_list_cmd_dnf5():
    assert return_group_list_cmd("dnf5") == ["dnf5", "group", "list", "--installed"]
