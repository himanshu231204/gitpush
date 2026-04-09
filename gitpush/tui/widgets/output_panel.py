"""Output panel widget for contextual logs and command results."""

from __future__ import annotations

import asyncio

from textual.widgets import LoadingIndicator, RichLog
from textual.containers import Vertical


class OutputPanel(Vertical):
    """Scrollable output area with loading and typing effects."""

    def compose(self):
        yield LoadingIndicator(id="output-loading")
        yield RichLog(id="output-log", wrap=True, highlight=True, markup=True)

    def on_mount(self) -> None:
        self.set_loading(False)

    def set_loading(self, is_loading: bool) -> None:
        """Toggle command loading indicator."""
        indicator = self.query_one("#output-loading", LoadingIndicator)
        indicator.display = is_loading

    def clear_output(self) -> None:
        """Clear output panel."""
        log = self.query_one("#output-log", RichLog)
        log.clear()

    def write_line(self, text: str = "") -> None:
        """Write a line immediately to output log."""
        log = self.query_one("#output-log", RichLog)
        log.write(text)

    async def type_lines(self, lines, delay: float = 0.01, max_chars: int = 1800) -> None:
        """Type lines with a subtle effect for AI-heavy outputs."""
        if not lines:
            return

        content = "\n".join(lines)
        if len(content) > max_chars:
            content = content[:max_chars] + "\n... output truncated for readability ..."

        for line in content.splitlines():
            self.write_line(line)
            await asyncio.sleep(delay)
