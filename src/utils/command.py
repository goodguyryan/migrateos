"""Subprocess wrapper"""

import subprocess
from typing import List, Tuple

# Try to run a command and tell you if it worked — never crashes your program even if the command fails or doesn't exist
def safe_run (args: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
    try:
        result = subprocess.run(args, 
                                capture_output=True, 
                                text=True, 
                                check=False,
                                timeout=timeout)

        return (result.returncode == 0, result.stdout, result.stderr)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return (False, "", str(e))

# Run a command that must work and return its output — crashes if anything goes wrong, because the answer is essential
def force_run (args: List[str], timeout: int = 30) -> str:
    result = subprocess.run(args, 
                            capture_output=True, 
                            text=True, 
                            check=True,
                            timeout=timeout)

    return result.stdout.strip()
