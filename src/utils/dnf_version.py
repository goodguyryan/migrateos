"""DNF version detection and command construction for DNF4 vs DNF5 compatibility.

TODO:
    - Implement detect_dnf_cmd() -> str (run dnf --version, parse output, return "dnf5" or "dnf")
    - Implement userinstalled_cmd(dnf_cmd: str) -> List[str] (returns [dnf, "repoquery", "--userinstalled", "--qf", "%{name}"])
    - Implement group_list_cmd(dnf_cmd: str) -> List[str] (returns [dnf, "group", "list", "--installed"]; add --ids for dnf4, omit for dnf5)
    - Fallback: if dnf --version fails, default to "dnf" (dnf4 behavior)
"""
