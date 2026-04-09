"""
Main CLI interface for run-git - Git Made Easy
"""

import click

from gitpush import __version__
from gitpush.config.settings import get_settings
from gitpush.ui.banner import show_banner
from gitpush.commands import (
    push,
    init_command,
    status,
    log,
    branch,
    switch,
    merge,
    remote,
    pull,
    sync,
    stash,
    undo,
    new,
    theme,
    graph,
    commit_ai,
    pr_ai,
    review_ai,
    ai_command,
    config_cmd,
    tag,
    release_command,
)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--version", "-v", is_flag=True, help="Show version")
def main(ctx, version):
    """run-git - Git Made Easy"""
    if version:
        click.echo(f"run-git version {__version__}")
        return

    if ctx.invoked_subcommand is None:
        show_banner()
        settings = get_settings()
        ui_layout = settings.get("ui_layout", "textual")

        if ui_layout == "legacy":
            from gitpush.ui.interactive import InteractiveUI

            InteractiveUI.main_menu()
            return

        try:
            from gitpush.tui.app import run_textual_app

            run_textual_app()
        except Exception:
            click.echo("Failed to launch Textual UI. Falling back to legacy menu.")
            from gitpush.ui.interactive import InteractiveUI

            InteractiveUI.main_menu()


# Register commands
main.add_command(push)
main.add_command(init_command)
main.add_command(status)
main.add_command(log)
main.add_command(branch)
main.add_command(switch)
main.add_command(merge)
main.add_command(remote)
main.add_command(pull)
main.add_command(sync)
main.add_command(stash)
main.add_command(undo)
main.add_command(new)
main.add_command(theme)
main.add_command(graph)
main.add_command(commit_ai)
main.add_command(pr_ai)
main.add_command(review_ai)
main.add_command(ai_command)
main.add_command(config_cmd)
main.add_command(tag)
main.add_command(release_command, name="release")


if __name__ == "__main__":
    main()
