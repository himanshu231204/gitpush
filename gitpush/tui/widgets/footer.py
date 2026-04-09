"""Footer widget with keyboard shortcuts."""

from textual.widgets import Static


class RunGitFooter(Static):
    """Bottom footer with keyboard hints."""

    def on_mount(self) -> None:
        self.update("↑/↓ navigate  Enter run  b back  / search  esc exit-search  q quit")
