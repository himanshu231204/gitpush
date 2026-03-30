"""
Custom exceptions for run-git CLI.
"""


class GitPushError(Exception):
    """Base exception for all GitPush errors."""

    pass


class GitNotFoundError(GitPushError):
    """Raised when Git is not installed or not in PATH."""

    pass


class NotARepositoryError(GitPushError):
    """Raised when the current directory is not a Git repository."""

    pass


class RemoteExistsError(GitPushError):
    """Raised when trying to add a remote that already exists."""

    pass


class RemoteNotFoundError(GitPushError):
    """Raised when a remote does not exist."""

    pass


class BranchExistsError(GitPushError):
    """Raised when trying to create a branch that already exists."""

    pass


class BranchNotFoundError(GitPushError):
    """Raised when a branch does not exist."""

    pass


class MergeConflictError(GitPushError):
    """Raised when a merge or pull results in conflicts."""

    pass


class CommitError(GitPushError):
    """Raised when a commit operation fails."""

    pass


class PushError(GitPushError):
    """Raised when pushing to remote fails."""

    pass


class PullError(GitPushError):
    """Raised when pulling from remote fails."""

    pass


class AuthenticationError(GitPushError):
    """Raised when authentication fails."""

    pass


class GitHubAPIError(GitPushError):
    """Raised when GitHub API operations fail."""

    pass


class ConfigurationError(GitPushError):
    """Raised when configuration is invalid or missing."""

    pass


class ValidationError(GitPushError):
    """Raised when input validation fails."""

    pass


class AIConfigurationError(GitPushError):
    """Raised when AI provider configuration is invalid or missing."""


class AIProviderError(GitPushError):
    """Raised when an AI provider request fails."""


class AIGenerationError(GitPushError):
    """Raised when generated AI content is missing or malformed."""


class AIDiffError(GitPushError):
    """Raised when git diff extraction/processing fails for AI features."""
