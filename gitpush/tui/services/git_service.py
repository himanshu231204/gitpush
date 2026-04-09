"""Service adapters that reuse existing git business logic for Textual UI."""

from __future__ import annotations

import os
from typing import Dict, List, Any

from gitpush.config.settings import get_settings
from gitpush.core.commit_generator import CommitGenerator
from gitpush.core.git_operations import GitOperations


class GitService:
    """Thin adapter over existing GitOperations for TUI command execution."""

    def __init__(self) -> None:
        self.git_ops = GitOperations()

    def get_repo_context(self) -> Dict[str, Any]:
        """Read repository context for header and assistant suggestions."""
        if not self.git_ops.is_git_repo() or self.git_ops.repo is None:
            return {
                "is_repo": False,
                "repo_name": "-",
                "branch": "-",
                "dirty_count": 0,
                "changed_files": [],
                "status_text": "Not a git repository",
            }

        working_dir = self.git_ops.repo.working_dir or ""
        repo_name = os.path.basename(working_dir.rstrip("\\/")) or "Unknown"
        status = self.git_ops.get_status() or {}

        changed_files = (
            status.get("staged", [])
            + status.get("modified", [])
            + status.get("untracked", [])
            + status.get("deleted", [])
        )
        dirty_count = len(changed_files)

        return {
            "is_repo": True,
            "repo_name": repo_name,
            "branch": status.get("branch", "main"),
            "dirty_count": dirty_count,
            "changed_files": changed_files,
            "status_text": "clean" if dirty_count == 0 else f"{dirty_count} changes",
        }

    def execute(self, command_id: str) -> Dict[str, Any]:
        """Execute a command by id and return structured output for UI rendering."""
        if command_id not in {
            "push",
            "commit",
            "branch",
            "merge",
            "stash",
            "pull",
            "ai-review",
            "pr-create",
        }:
            return {
                "ok": False,
                "title": command_id,
                "lines": [f"Unknown command: {command_id}"],
            }

        if command_id in {"ai-review", "pr-create"}:
            return {
                "ok": True,
                "title": command_id,
                "lines": [
                    "Delegating to AI service...",
                ],
                "delegate": True,
            }

        if not self.git_ops.is_git_repo():
            return {
                "ok": False,
                "title": command_id,
                "lines": ["Not a git repository. Run 'run-git init' first."],
            }

        handlers = {
            "push": self._cmd_push,
            "commit": self._cmd_commit,
            "branch": self._cmd_branch,
            "merge": self._cmd_merge,
            "stash": self._cmd_stash,
            "pull": self._cmd_pull,
        }
        return handlers[command_id]()

    def _cmd_push(self) -> Dict[str, Any]:
        lines: List[str] = ["Running push workflow..."]
        if not self.git_ops.add_all():
            return {"ok": False, "title": "push", "lines": lines + ["Failed to add files."]}

        message = CommitGenerator(self.git_ops.repo).generate_message()
        lines.append(f"Commit message: {message}")

        if not self.git_ops.commit(message):
            return {"ok": False, "title": "push", "lines": lines + ["Commit failed."]}

        pull_ok = self.git_ops.pull()
        push_ok = self.git_ops.push()
        lines.append("Pull complete." if pull_ok else "Pull failed.")
        lines.append("Push complete." if push_ok else "Push failed.")

        return {
            "ok": pull_ok and push_ok,
            "title": "push",
            "lines": lines,
        }

    def _cmd_commit(self) -> Dict[str, Any]:
        lines: List[str] = ["Generating commit from current changes..."]

        if not self.git_ops.add_all():
            return {"ok": False, "title": "commit", "lines": lines + ["Failed to add files."]}

        message = CommitGenerator(self.git_ops.repo).generate_message()
        lines.append(f"Commit message: {message}")

        ok = self.git_ops.commit(message)
        lines.append("Commit complete." if ok else "Commit failed.")

        return {
            "ok": ok,
            "title": "commit",
            "lines": lines,
        }

    def _cmd_branch(self) -> Dict[str, Any]:
        branches = self.git_ops.get_branches()
        current = self.git_ops.repo.active_branch.name if self.git_ops.repo else "main"

        lines: List[str] = [f"Current branch: {current}", "", "Branches:"]
        for name in branches:
            prefix = "*" if name == current else "-"
            lines.append(f"{prefix} {name}")

        return {
            "ok": True,
            "title": "branch",
            "lines": lines,
        }

    def _cmd_merge(self) -> Dict[str, Any]:
        settings = get_settings()
        target = settings.get("default_branch", "main")
        current = self.git_ops.repo.active_branch.name if self.git_ops.repo else ""

        if current == target:
            return {
                "ok": False,
                "title": "merge",
                "lines": [f"Already on default branch '{target}'. Switch to another branch first."],
            }

        try:
            self.git_ops.repo.git.merge(target)
            return {
                "ok": True,
                "title": "merge",
                "lines": [f"Merged '{target}' into '{current}'."],
            }
        except Exception as exc:
            return {
                "ok": False,
                "title": "merge",
                "lines": [f"Merge failed: {exc}"],
            }

    def _cmd_stash(self) -> Dict[str, Any]:
        try:
            self.git_ops.repo.git.stash()
            return {"ok": True, "title": "stash", "lines": ["Changes stashed successfully."]}
        except Exception as exc:
            return {"ok": False, "title": "stash", "lines": [f"Stash failed: {exc}"]}

    def _cmd_pull(self) -> Dict[str, Any]:
        ok = self.git_ops.pull()
        return {
            "ok": ok,
            "title": "pull",
            "lines": ["Pull complete." if ok else "Pull failed."],
        }
