"""Path safety checks: blocklist, exclusions, secret detection, runtime detection, include scanning."""

from pathlib import Path
import fnmatch
from typing import List, Optional
from src.utils.constants import (BLOCKED_EXACT, 
                                 BLOCKED_PREFIXES, 
                                 EXACT_EXCLUDE, 
                                 GLOB_EXCLUDE, 
                                 SECRET_NAME_PATTERNS, 
                                 SECRET_EXTENSIONS, 
                                 SECRET_CONTENT_RE,
                                 RUNTIME_MARKERS, 
                                 INSTALL_COMMANDS,
                                 INCLUDE_RE
)

def is_blocked_path(path: Path) -> bool:
    normalized = str(path.as_posix())

    if normalized in BLOCKED_EXACT:
        return True
    for prefix in BLOCKED_PREFIXES:
        if normalized.startswith(prefix):
            return True

    return False

def is_excluded_file(filename: str) -> bool:
    if filename in EXACT_EXCLUDE:
        return True
    for pattern in GLOB_EXCLUDE:
        if fnmatch.fnmatch(filename, pattern):
            return True

    return False

def is_secret_file(filename: str) -> bool:
    filename_lower = filename.lower()
  
    for pattern in SECRET_NAME_PATTERNS:
        if pattern in filename_lower and not filename_lower.endswith(".pub"):
            return True
    
    for ext in SECRET_EXTENSIONS:
        if filename_lower.endswith(ext):
            return True
    
    return False

def detect_secrets_in_file(content: str) -> List[str]:
    matches = SECRET_CONTENT_RE.findall(content)
    return [f"{m[0]}={m[2]}" for m in matches]

def detect_runtime(dir: Path) -> Optional[str]:
    found = set()
    for marker, runtime in RUNTIME_MARKERS.items():
        if (dir / marker).exists():
            found.add(runtime)
    
    if len(found) == 1:
        return found.pop()
    elif len(found) > 1:
        return "multiple"
    
    return None

def suggest_install(runtime: str) -> List[str]:
    return INSTALL_COMMANDS.get(runtime, [])

# Find include directives in config file and extract reference path
def detect_includes(content: str) -> List[str]:
    return [p.rstrip(";") for p in INCLUDE_RE.findall(content)]
