"""Safe subprocess wrapper — never shell=True.

TODO:
    - Implement run(args: List[str], check=False, timeout=30) -> CompletedProcess
    - Implement run_ok(args: List[str], timeout=30) -> Tuple[bool, str, str]  (never raises)
    - Implement run_output(args: List[str], timeout=30) -> str  (raises on failure, returns stripped stdout)
    - Ensure subprocess.run is called with shell=False and timeout is enforced
"""
