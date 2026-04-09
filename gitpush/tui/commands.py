"""Command definitions for the Textual command palette."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CommandSpec:
    """Command metadata shown in the command palette."""

    command_id: str
    label: str
    description: str
    category: str = "core"


PALETTE_COMMANDS: List[CommandSpec] = [
    CommandSpec("push", "push", "Add, commit, pull, and push changes", "git"),
    CommandSpec("commit", "commit", "Create AI-assisted commit from current changes", "git"),
    CommandSpec("branch", "branch", "List branches and show current branch", "git"),
    CommandSpec("merge", "merge", "Merge default branch into current branch", "git"),
    CommandSpec("stash", "stash", "Stash working directory changes", "git"),
    CommandSpec("pull", "pull", "Pull latest changes from remote", "git"),
    CommandSpec("ai-review", "ai-review", "Generate AI review from branch diff", "ai"),
    CommandSpec("pr-create", "pr-create", "Generate AI PR description", "ai"),
]
