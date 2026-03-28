"""
Status and log commands for gitpush.
"""
import click

from gitpush.core.git_operations import GitOperations
from gitpush.ui.banner import show_error, show_info
from gitpush.ui.interactive import InteractiveUI


@click.command()
def status():
    """Show repository status"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    status = git_ops.get_status()
    if status:
        InteractiveUI.show_status_table(status)


@click.command()
@click.option('--max', default=10, help='Maximum number of commits')
@click.option('--graph', is_flag=True, help='Show graph')
def log(max, graph):
    """Show commit history"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    commits = git_ops.get_log(max_count=max)
    if commits:
        InteractiveUI.show_log_table(commits)
    else:
        show_info("No commits yet")
