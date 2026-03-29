"""Tests for core AI engine orchestration."""

import unittest

from gitpush.ai.config import AIConfig
from gitpush.core.ai_engine import AIEngine
from gitpush.exceptions import AIDiffError, NotARepositoryError


class FakeGitOps:
    """Minimal GitOperations test double."""

    def __init__(
        self,
        is_repo=True,
        staged_diff="",
        working_diff="",
        branch_diff="",
        commit_messages=None,
    ):
        self._is_repo = is_repo
        self._staged = staged_diff
        self._working = working_diff
        self._branch = branch_diff
        self._messages = commit_messages or ["feat: add feature"]

    def is_git_repo(self):
        return self._is_repo

    def get_staged_diff(self):
        return self._staged

    def get_working_diff(self):
        return self._working

    def get_branch_diff(self, base_branch="main", head_ref="HEAD"):
        return self._branch

    def get_recent_commit_messages(self, limit=5):
        return self._messages[:limit]


class FakeAIClient:
    """AIClient test double."""

    def __init__(self):
        self.last_diff = None
        self.last_commits = None

    def generate_commit_message(self, cleaned_diff):
        self.last_diff = cleaned_diff
        return "feat(core): add ai flow\n\n- add ai engine"

    def generate_pr_description(self, cleaned_diff, commit_messages):
        self.last_diff = cleaned_diff
        self.last_commits = commit_messages
        return "## Summary\nAI PR description"

    def generate_review(self, cleaned_diff):
        self.last_diff = cleaned_diff
        return "⚠️ Bug:\nNone"


class TestAIEngine(unittest.TestCase):
    """AIEngine behavior tests."""

    def test_commit_uses_staged_diff(self):
        git_ops = FakeGitOps(staged_diff="diff --git a/a.py b/a.py\n+line")
        ai_client = FakeAIClient()
        engine = AIEngine(
            git_ops=git_ops,
            ai_client=ai_client,
            config=AIConfig(provider="local"),
        )

        result = engine.generate_commit_message()
        self.assertIn("feat(core)", result)
        self.assertIsNotNone(ai_client.last_diff)

    def test_commit_falls_back_to_working_diff(self):
        git_ops = FakeGitOps(staged_diff="", working_diff="diff --git a/b.py b/b.py\n+line")
        ai_client = FakeAIClient()
        engine = AIEngine(
            git_ops=git_ops,
            ai_client=ai_client,
            config=AIConfig(provider="local"),
        )

        result = engine.generate_commit_message()
        self.assertIn("feat(core)", result)

    def test_commit_raises_for_empty_diff(self):
        git_ops = FakeGitOps(staged_diff="", working_diff="")
        engine = AIEngine(
            git_ops=git_ops,
            ai_client=FakeAIClient(),
            config=AIConfig(provider="local"),
        )

        with self.assertRaises(AIDiffError):
            engine.generate_commit_message()

    def test_pr_generation_uses_branch_diff_and_commits(self):
        git_ops = FakeGitOps(
            branch_diff="diff --git a/c.py b/c.py\n+line",
            commit_messages=["feat: x", "fix: y"],
        )
        ai_client = FakeAIClient()
        engine = AIEngine(
            git_ops=git_ops,
            ai_client=ai_client,
            config=AIConfig(provider="local"),
        )

        result = engine.generate_pr_description(base_branch="main", head_ref="HEAD", commit_limit=2)
        self.assertIn("## Summary", result)
        self.assertEqual(ai_client.last_commits, ["feat: x", "fix: y"])

    def test_review_generation(self):
        git_ops = FakeGitOps(branch_diff="diff --git a/d.py b/d.py\n+line")
        engine = AIEngine(
            git_ops=git_ops,
            ai_client=FakeAIClient(),
            config=AIConfig(provider="local"),
        )

        result = engine.generate_review(base_branch="main", head_ref="HEAD")
        self.assertIn("⚠️ Bug", result)

    def test_non_repo_raises(self):
        git_ops = FakeGitOps(is_repo=False)
        engine = AIEngine(
            git_ops=git_ops,
            ai_client=FakeAIClient(),
            config=AIConfig(provider="local"),
        )

        with self.assertRaises(NotARepositoryError):
            engine.generate_review()


if __name__ == "__main__":
    unittest.main()
