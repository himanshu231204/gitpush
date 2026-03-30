"""
File operation utilities.
"""

import os
import fnmatch
from typing import List

SENSITIVE_PATTERNS = [
    ".env",
    ".env.local",
    "*.pem",
    "*.key",
    "*.secret",
    "*.credentials",
    "secrets.yaml",
    "secrets.json",
]


def get_changed_files(repo) -> List[str]:
    """Get list of changed files in the repository."""
    changed = []
    if repo.index.diff(None):
        for diff in repo.index.diff(None):
            changed.append(diff.a_path or diff.b_path)
    if repo.untracked_files:
        changed.extend(repo.untracked_files)
    return list(set(changed))


def is_sensitive_file(filepath: str) -> bool:
    """Check if a file is sensitive."""
    filename = os.path.basename(filepath)
    for pattern in SENSITIVE_PATTERNS:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def find_sensitive_files(path: str = ".") -> List[str]:
    """Find sensitive files in the given path."""
    sensitive = []
    for root, dirs, files in os.walk(path):
        if ".git" in root:
            continue
        for filename in files:
            filepath = os.path.join(root, filename)
            if is_sensitive_file(filepath):
                sensitive.append(filepath)
    return sensitive
