"""Core AI orchestration for commit/pr/review features."""

from __future__ import annotations

from typing import Optional

from gitpush.ai.client import AIClient
from gitpush.ai.config import AIConfig
from gitpush.core.git_operations import GitOperations
from gitpush.exceptions import AIDiffError, NotARepositoryError
from gitpush.utils.diff_cleaner import DiffCleaner


class AIEngine:
    """Coordinate Git input, diff cleaning, and AI generation."""

    def __init__(
        self,
        git_ops: Optional[GitOperations] = None,
        ai_client: Optional[AIClient] = None,
        diff_cleaner: Optional[DiffCleaner] = None,
        config: Optional[AIConfig] = None,
    ) -> None:
        self.config = config or AIConfig.from_env()
        self.git_ops = git_ops or GitOperations()
        self.ai_client = ai_client or AIClient(config=self.config)
        self.diff_cleaner = diff_cleaner or DiffCleaner()

    def generate_commit_message(self) -> str:
        """Generate conventional commit message from staged/fallback diff."""

        self._ensure_repo()

        raw_diff = self.git_ops.get_staged_diff()
        if not raw_diff.strip():
            raw_diff = self.git_ops.get_working_diff()

        cleaned = self._prepare_diff(
            raw_diff=raw_diff,
            max_chars=self.config.max_commit_diff_chars,
        )
        return self.ai_client.generate_commit_message(cleaned)

    def generate_pr_description(
        self,
        base_branch: Optional[str] = None,
        head_ref: str = "HEAD",
        commit_limit: Optional[int] = None,
    ) -> str:
        """Generate PR description from branch diff and commit history."""

        self._ensure_repo()

        resolved_base = base_branch or self.config.default_base_branch
        raw_diff = self.git_ops.get_branch_diff(base_branch=resolved_base, head_ref=head_ref)
        cleaned = self._prepare_diff(raw_diff=raw_diff, max_chars=self.config.max_pr_diff_chars)
        limit = commit_limit or self.config.default_commit_history_limit
        commit_messages = self.git_ops.get_recent_commit_messages(limit=limit)

        return self.ai_client.generate_pr_description(cleaned, commit_messages)

    def generate_review(self, base_branch: Optional[str] = None, head_ref: str = "HEAD") -> str:
        """Generate AI review feedback from branch diff."""

        self._ensure_repo()

        resolved_base = base_branch or self.config.default_base_branch
        raw_diff = self.git_ops.get_branch_diff(base_branch=resolved_base, head_ref=head_ref)
        cleaned = self._prepare_diff(raw_diff=raw_diff, max_chars=self.config.max_pr_diff_chars)

        return self.ai_client.generate_review(cleaned)

    def _prepare_diff(self, raw_diff: str, max_chars: int) -> str:
        prepared = self.diff_cleaner.prepare_for_ai(
            raw_diff=raw_diff,
            max_chars=max_chars,
            chunk_size=self.config.chunk_size,
        )
        if self.diff_cleaner.is_empty(prepared):
            raise AIDiffError("No diff content found for AI analysis")
        return prepared

    def _ensure_repo(self) -> None:
        if not self.git_ops.is_git_repo():
            raise NotARepositoryError("Not a git repository")
