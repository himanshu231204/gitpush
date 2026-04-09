"""AI service adapter for Textual UI, reusing AIEngine."""

from __future__ import annotations

from typing import Dict, List, Any

from gitpush.config.settings import get_settings
from gitpush.core.ai_engine import AIEngine
from gitpush.core.git_operations import GitOperations


class AIService:
    """Thin adapter that calls existing AI engine methods."""

    def __init__(self) -> None:
        self.git_ops = GitOperations()

    def suggest_next_actions(self, repo_context: Dict[str, Any]) -> List[str]:
        """Simple assistant suggestions based on repository state."""
        if not repo_context.get("is_repo"):
            return [
                "Initialize a repository with: run-git init",
                "Or open this app inside an existing git repository.",
            ]

        dirty_count = repo_context.get("dirty_count", 0)
        if dirty_count == 0:
            return [
                "Working tree is clean. Consider pulling latest changes.",
                "Start a new branch for your next task.",
            ]

        return [
            "You have pending changes. Run 'commit' to snapshot work.",
            "Use 'ai-review' before pushing for quick quality checks.",
            "Run 'push' when ready to publish updates.",
        ]

    def execute(self, command_id: str) -> Dict[str, Any]:
        """Execute AI-driven command paths."""
        if not self.git_ops.is_git_repo():
            return {
                "ok": False,
                "title": command_id,
                "lines": ["Not a git repository. Run 'run-git init' first."],
            }

        settings = get_settings()
        engine = AIEngine(git_ops=self.git_ops)

        if command_id == "ai-review":
            base = settings.get("ai_default_base_branch", "main")
            try:
                review = engine.generate_review(base_branch=base, head_ref="HEAD")
                return {
                    "ok": True,
                    "title": "ai-review",
                    "lines": [f"Diff: {base}...HEAD", "", review],
                }
            except Exception as exc:
                return {
                    "ok": False,
                    "title": "ai-review",
                    "lines": [f"AI review failed: {exc}"],
                }

        if command_id == "pr-create":
            base = settings.get("ai_default_base_branch", "main")
            try:
                description = engine.generate_pr_description(
                    base_branch=base,
                    head_ref="HEAD",
                    commit_limit=settings.get("ai_default_commit_history_limit", 8),
                )
                return {
                    "ok": True,
                    "title": "pr-create",
                    "lines": [f"Diff: {base}...HEAD", "", description],
                }
            except Exception as exc:
                return {
                    "ok": False,
                    "title": "pr-create",
                    "lines": [f"PR generation failed: {exc}"],
                }

        return {
            "ok": False,
            "title": command_id,
            "lines": [f"Unsupported AI command: {command_id}"],
        }
