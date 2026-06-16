"""DNF version detection and command construction for DNF4 vs DNF5 compatibility.

TODO:
    - Implement detect_dnf_cmd() -> str (run dnf --version, parse output, return "dnf5" or "dnf")
    - Implement userinstalled_cmd(dnf_cmd: str) -> List[str] (returns [dnf, "repoquery", "--userinstalled", "--qf", "%{name}"])
    - Implement group_list_cmd(dnf_cmd: str) -> List[str] (returns [dnf, "group", "list", "--installed"]; add --ids for dnf4, omit for dnf5)
    - Fallback: if dnf --version fails, default to "dnf" (dnf4 behavior)
"""
from src.utils.command import safe_run
from typing import List

def detect_dnf_version() -> str:
    ok, stdout, _ = safe_run(["dnf", "--version"])

    if ok and "detect_dnf_version" in stdout.lower():
        return "dnf5"
    return "dnf"

def return_userinstalled_cmd(dnf_cmd: str) -> List[str]:
    return [dnf_cmd, "repoquery", "--userinstalled", "--qf", "%{name}"]

def return_group_list_cmd(dnf_cmd: str) -> List[str]:
    cmd = [dnf_cmd, "group", "list", "--installed"]
    if dnf_cmd == "dnf":
        cmd.append("--ids")
    return cmd
