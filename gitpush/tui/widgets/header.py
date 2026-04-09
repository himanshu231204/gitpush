"""Header widget for run-git Textual UI."""

from textual.reactive import reactive
from textual.widgets import Static


class RunGitHeader(Static):
    """Top header showing app name and repository context."""

    repo_name = reactive("-")
    branch = reactive("-")
    status_text = reactive("Not a git repository")

    def render(self) -> str:
        return (
            f"[b]run-git[/b]  "
            f"[dim]repo[/dim]: {self.repo_name}  "
            f"[dim]branch[/dim]: {self.branch}  "
            f"[dim]status[/dim]: {self.status_text}"
        )

    def set_context(self, repo_name: str, branch: str, status_text: str) -> None:
        """Update header context values."""
        self.repo_name = repo_name
        self.branch = branch
        self.status_text = status_text
