"""Main Textual application for run-git."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

from gitpush.tui.commands import PALETTE_COMMANDS, CommandSpec
from gitpush.tui.services.ai_service import AIService
from gitpush.tui.services.git_service import GitService
from gitpush.tui.widgets.command_palette import CommandPalette
from gitpush.tui.widgets.footer import RunGitFooter
from gitpush.tui.widgets.header import RunGitHeader
from gitpush.tui.widgets.output_panel import OutputPanel


class RunGitApp(App):
    """Claude-style modern terminal UI for run-git."""

    CSS_PATH = "styles.tcss"
    TITLE = "run-git"

    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("enter", "execute", "Run", show=False),
        Binding("b", "back", "Back", show=False),
        Binding("slash", "search", "Search", show=False),
        Binding("escape", "exit_search", "Exit Search", show=False),
        Binding("q", "quit", "Quit", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.git_service = GitService()
        self.ai_service = AIService()

    def compose(self) -> ComposeResult:
        yield RunGitHeader(id="app-header")
        with Horizontal(id="main-layout"):
            with Vertical(id="sidebar"):
                yield CommandPalette(PALETTE_COMMANDS, id="command-palette")
            with Vertical(id="content"):
                yield OutputPanel(id="output-panel")
        yield RunGitFooter(id="app-footer")

    async def on_mount(self) -> None:
        self.refresh_context()
        output = self.query_one(OutputPanel)
        output.write_line("Welcome to run-git Textual UI.")
        output.write_line("Use / to search commands and Enter to execute.")
        self.show_assistant_suggestions()
        self.set_interval(5.0, self.refresh_context)

    def refresh_context(self) -> None:
        """Refresh header from current repository context."""
        context = self.git_service.get_repo_context()
        header = self.query_one(RunGitHeader)
        header.set_context(
            repo_name=context.get("repo_name", "-"),
            branch=context.get("branch", "-"),
            status_text=context.get("status_text", "unknown"),
        )

    def show_assistant_suggestions(self) -> None:
        """Render assistant suggestions from repo state."""
        context = self.git_service.get_repo_context()
        suggestions = self.ai_service.suggest_next_actions(context)

        output = self.query_one(OutputPanel)
        output.write_line("")
        output.write_line("Assistant suggestions:")
        for item in suggestions:
            output.write_line(f"- {item}")

    async def run_command(self, command: CommandSpec) -> None:
        """Execute command without blocking the UI event loop."""
        output = self.query_one(OutputPanel)
        output.set_loading(True)
        output.write_line("")
        output.write_line(f"[bold]> {command.label}[/bold]")

        result = await asyncio.to_thread(self.git_service.execute, command.command_id)
        if result.get("delegate"):
            result = await asyncio.to_thread(self.ai_service.execute, command.command_id)

        lines = result.get("lines", [])
        await output.type_lines(lines)

        status_text = "OK" if result.get("ok") else "FAILED"
        output.write_line(f"[dim]Status: {status_text}[/dim]")
        output.set_loading(False)

        self.refresh_context()

    def action_cursor_up(self) -> None:
        self.query_one(CommandPalette).move_selection(-1)

    def action_cursor_down(self) -> None:
        self.query_one(CommandPalette).move_selection(1)

    async def action_execute(self) -> None:
        palette = self.query_one(CommandPalette)
        command = palette.get_active_command()
        if command:
            await self.run_command(command)

    def action_back(self) -> None:
        palette = self.query_one(CommandPalette)
        palette.exit_search_mode()
        output = self.query_one(OutputPanel)
        output.write_line("[dim]Back: search reset.[/dim]")

    def action_search(self) -> None:
        self.query_one(CommandPalette).enter_search_mode()

    def action_exit_search(self) -> None:
        self.query_one(CommandPalette).exit_search_mode()

    async def on_command_palette_command_chosen(
        self, message: CommandPalette.CommandChosen
    ) -> None:
        await self.run_command(message.command)


def run_textual_app() -> None:
    """Entrypoint for launching the Textual app."""
    RunGitApp().run()
