"""
Remote, pull, and sync commands for gitpush.
"""
import click

from gitpush.core.git_operations import GitOperations
from gitpush.ui.banner import show_error, show_info, show_success


@click.command()
@click.argument('name', required=False)
@click.option('--add', help='Add remote URL')
@click.option('--remove', is_flag=True, help='Remove remote')
def remote(name, add, remove):
    """Manage remote repositories"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    if add:
        git_ops.add_remote(name or "origin", add)
    elif remove:
        try:
            git_ops.repo.delete_remote(name or "origin")
            show_success(f"Remote '{name or 'origin'}' removed")
        except Exception as e:
            show_error(f"Failed to remove remote: {str(e)}")
    else:
        remotes = git_ops.repo.remotes
        if remotes:
            show_info("Remote repositories:")
            for r in remotes:
                click.echo(f"  {r.name}: {r.url}")
        else:
            show_info("No remote repositories configured")


@click.command()
def pull():
    """Pull changes from remote"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    git_ops.pull()


@click.command()
def sync():
    """Sync with remote (pull + push)"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    if git_ops.pull():
        git_ops.push()
