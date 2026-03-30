"""
Output formatting utilities.
"""

from typing import List, Dict, Any


def format_commit_message(changed_files: List[str], prefix: str = "Update") -> str:
    """Format a commit message based on changed files."""
    if not changed_files:
        return f"{prefix}: no files"
    if len(changed_files) == 1:
        return f"{prefix}: {changed_files[0]}"
    if len(changed_files) <= 3:
        return f"{prefix}: {', '.join(changed_files)}"
    return f"{prefix}: {', '.join(changed_files[:3])} and {len(changed_files) - 3} more"


def format_branch_list(branches: List[Dict[str, Any]]) -> str:
    """Format branch list for display."""
    if not branches:
        return "No branches found"
    lines = []
    for branch in branches:
        name = branch.get("name", "")
        current = branch.get("current", False)
        prefix = "*" if current else " "
        lines.append(f"{prefix} {name}")
    return "\n".join(lines)


def format_remote_list(remotes: List[Dict[str, str]]) -> str:
    """Format remote list for display."""
    if not remotes:
        return "No remotes found"
    lines = []
    for remote in remotes:
        name = remote.get("name", "")
        url = remote.get("url", "")
        lines.append(f"{name}\t{url}")
    return "\n".join(lines)
