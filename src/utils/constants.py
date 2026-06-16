"""Shared constants for MigrateOS utilities."""
import re

# Blocklist

BLOCKED_EXACT = {
    "/etc/machine-id", "/etc/hostname", "/etc/hosts", "/etc/fstab",
    "/etc/shadow", "/etc/gshadow", "/etc/passwd", "/etc/group",
    "/etc/crypttab", "/etc/resolv.conf",
}

BLOCKED_PREFIXES = (
    "/etc/ssh/ssh_host_", "/var/log/", "/tmp/", "/run/",
    "/proc/", "/sys/", "/dev/",
)

# Exclusions

EXACT_EXCLUDE = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    "target", "build", "dist", "tmp", "cache",
}

GLOB_EXCLUDE = [
    "*.swp", "*.swo", "*~", "*.bak", "*.rpmnew", "*.rpmsave",
    "*.orig", "*.pyc", "*.log", "*.sock", "*.pid",
]

# Secret filenames (Tier 1)

SECRET_NAME_PATTERNS = [
    ".env", "key", "secret", "token", "credential", "private",
    "id_rsa", "id_ed25519", "id_ecdsa", "tls.key", "server.key",
]

SECRET_EXTENSIONS = {".pem", ".key"}

# Secret content keys (Tier 2)

SECRET_KEY_NAMES = (
    "PASSWORD|SECRET|TOKEN|API_KEY|PRIVATE_KEY|DATABASE_URL|"
    "JWT_SECRET|ENCRYPTION_KEY|ACCESS_KEY|SECRET_KEY|DB_PASSWORD|VAULT_TOKEN"
)

SECRET_CONTENT_RE = re.compile(
    r'(?i)(' + SECRET_KEY_NAMES + r')\s*[:=]\s*(["\' ]*)(\S{4,})',
    re.MULTILINE,
)

# Runtime detection

RUNTIME_MARKERS = {
    "package.json": "node",
    "requirements.txt": "python",
    "pyproject.toml": "python",
    "setup.py": "python",
    "pom.xml": "java",
    "build.gradle": "java",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "Gemfile": "ruby",
    "composer.json": "php",
}

# Install suggestions 

INSTALL_COMMANDS = {
    "node":   ["dnf install nodejs npm", "npm install"],
    "python": ["dnf install python3 python3-pip", "pip install -r requirements.txt"],
    "java":   ["dnf install java-11-openjdk", "mvn install"],
    "go":     ["dnf install golang", "go mod download"],
    "rust":   ["curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"],
    "ruby":   ["dnf install ruby", "bundle install"],
    "php":    ["dnf install php", "composer install"],
}

INCLUDE_RE = re.compile(
    r'^\s*(?:include|Include(?:Optional)?|#includedir|\$IncludeConfig|\.include)\s+(\S+)',
    re.MULTILINE,
)