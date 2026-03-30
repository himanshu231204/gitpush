"""
Input validation utilities.
"""

from gitpush.exceptions import ValidationError


def validate_branch_name(name: str) -> bool:
    """Validate Git branch name."""
    if not name:
        raise ValidationError("Branch name cannot be empty")
    invalid_chars = [" ", "~", "^", ":", "\\", "*", "?", "["]
    for char in invalid_chars:
        if char in name:
            raise ValidationError(f"Branch name cannot contain '{char}'")
    if name.startswith("/") or name.endswith("/"):
        raise ValidationError("Branch name cannot start or end with '/'")
    return True


def validate_remote_name(name: str) -> bool:
    """Validate remote name."""
    if not name:
        raise ValidationError("Remote name cannot be empty")
    invalid_chars = [" ", "~", "^", ":", "\\", "*", "?", "["]
    for char in invalid_chars:
        if char in name:
            raise ValidationError(f"Remote name cannot contain '{char}'")
    return True


def validate_repo_url(url: str) -> bool:
    """Validate Git repository URL."""
    if not url:
        raise ValidationError("Repository URL cannot be empty")
    return True


def validate_commit_message(message: str) -> bool:
    """Validate commit message."""
    if not message or not message.strip():
        raise ValidationError("Commit message cannot be empty")
    if len(message) > 5000:
        raise ValidationError("Commit message too long (max 5000 characters)")
    return True
