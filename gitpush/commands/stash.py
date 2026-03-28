"""
Stash and undo commands for gitpush.
"""
import click

from gitpush.core.git_operations import GitOperations
from gitpush.ui.banner import show_error, show_success
from gitpush.ui.interactive import InteractiveUI


@click.command()
def stash():
    """Stash current changes"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    try:
        git_ops.repo.git.stash()
        show_success("Changes stashed")
    except Exception as e:
        show_error(f"Failed to stash: {str(e)}")


@click.command()
def undo():
    """Undo last commit (keep changes)"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    if InteractiveUI.confirm_action("Undo last commit? (changes will be kept)"):
        try:
            git_ops.repo.git.reset('HEAD~1', soft=True)
            show_success("Last commit undone (changes kept)")
        except Exception as e:
            show_error(f"Failed to undo: {str(e)}")
