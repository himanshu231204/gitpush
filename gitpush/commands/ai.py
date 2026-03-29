"""AI assistant interactive menu command."""

import click


@click.command(name="ai")
def ai_command() -> None:
    """Open the interactive AI assistant menu."""
    from gitpush.ui.interactive import InteractiveUI

    InteractiveUI.ai_menu()
