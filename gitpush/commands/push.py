"""
Push command for gitpush.
"""

import click

from gitpush.core.git_operations import GitOperations
from gitpush.core.commit_generator import CommitGenerator
from gitpush.ui.banner import show_info, show_error
from gitpush.ui.interactive import InteractiveUI


@click.command()
@click.option("-m", "--message", help="Commit message")
@click.option("--force", is_flag=True, help="Force push")
@click.option("--dry-run", is_flag=True, help="Show what will happen")
def push(message, force, dry_run):
    """Quick push: add, commit, pull, push"""
    git_ops = GitOperations()

    if dry_run:
        show_info("Dry run mode - showing what will happen:")
        status = git_ops.get_status()
        if status:
            InteractiveUI.show_status_table(status)
        return

    if not git_ops.is_git_repo():
        show_error("Not a git repository. Run 'run-git init' first")
        return

    if not git_ops.add_all():
        return

    if not message:
        generator = CommitGenerator(git_ops.repo)
        message = generator.generate_message()
        show_info(f"Auto-generated message: {message}")

    if not git_ops.commit(message):
        return

    git_ops.pull()
    git_ops.push(force=force)
