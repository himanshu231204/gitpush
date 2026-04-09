"""Searchable command palette widget for run-git Textual UI."""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

from gitpush.tui.commands import CommandSpec


class CommandPalette(Vertical):
    """Left sidebar palette with fuzzy search and keyboard selection."""

    class CommandChosen(Message):
        """Message emitted when user chooses a command."""

        def __init__(self, command: CommandSpec) -> None:
            self.command = command
            super().__init__()

    def __init__(self, commands: List[CommandSpec], **kwargs) -> None:
        super().__init__(**kwargs)
        self._commands = commands
        self._filtered = list(commands)

    def compose(self) -> ComposeResult:
        yield Input(placeholder="/ search commands", id="command-search")
        yield OptionList(id="command-list")

    def on_mount(self) -> None:
        search = self.query_one("#command-search", Input)
        search.display = False
        self.refresh_options()

    def refresh_options(self) -> None:
        """Rebuild option list from current filtered commands."""
        option_list = self.query_one("#command-list", OptionList)
        option_list.clear_options()

        options = [
            Option(f"{cmd.label:<10} {cmd.description}", id=cmd.command_id)
            for cmd in self._filtered
        ]
        option_list.add_options(options)

        if self._filtered:
            option_list.highlighted = 0

    def enter_search_mode(self) -> None:
        """Show search box and focus it."""
        search = self.query_one("#command-search", Input)
        search.display = True
        search.focus()

    def exit_search_mode(self) -> None:
        """Hide search box and reset focus to options."""
        search = self.query_one("#command-search", Input)
        option_list = self.query_one("#command-list", OptionList)

        search.display = False
        search.value = ""
        self._filtered = list(self._commands)
        self.refresh_options()
        option_list.focus()

    def move_selection(self, direction: int) -> None:
        """Move active selection up/down by direction step."""
        option_list = self.query_one("#command-list", OptionList)
        if option_list.option_count == 0:
            return

        current = option_list.highlighted or 0
        next_index = max(0, min(option_list.option_count - 1, current + direction))
        option_list.highlighted = next_index

    def get_active_command(self) -> CommandSpec | None:
        """Get command represented by current highlighted option."""
        option_list = self.query_one("#command-list", OptionList)
        if option_list.option_count == 0:
            return None

        index = option_list.highlighted or 0
        if index >= len(self._filtered):
            return None
        return self._filtered[index]

    def choose_active(self) -> None:
        """Emit selection message for currently highlighted command."""
        active = self.get_active_command()
        if active is not None:
            self.post_message(self.CommandChosen(active))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Instant fuzzy filtering while typing."""
        if event.input.id != "command-search":
            return

        query = event.value.strip().lower()
        if not query:
            self._filtered = list(self._commands)
            self.refresh_options()
            return

        self._filtered = [
            cmd
            for cmd in self._commands
            if self._fuzzy_match(query, f"{cmd.label} {cmd.description}")
        ]
        self.refresh_options()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle Enter on option list."""
        option_id = event.option.id
        if not option_id:
            return

        for command in self._filtered:
            if command.command_id == option_id:
                self.post_message(self.CommandChosen(command))
                break

    @staticmethod
    def _fuzzy_match(query: str, candidate: str) -> bool:
        """Simple subsequence fuzzy matching."""
        candidate = candidate.lower()
        pos = 0
        for char in query:
            pos = candidate.find(char, pos)
            if pos == -1:
                return False
            pos += 1
        return True
