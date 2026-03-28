"""
Branch, switch, and merge commands for gitpush.
"""
import click

from gitpush.core.git_operations import GitOperations
from gitpush.core.conflict_resolver import ConflictResolver
from gitpush.ui.banner import show_error, show_info, show_success
from gitpush.ui.interactive import InteractiveUI


@click.command()
@click.argument('name', required=False)
@click.option('-d', '--delete', help='Delete branch')
def branch(name, delete):
    """Branch operations"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    if delete:
        git_ops.delete_branch(delete)
    elif name:
        git_ops.create_branch(name)
        if InteractiveUI.confirm_action("Switch to new branch?"):
            git_ops.switch_branch(name)
    else:
        branches = git_ops.get_branches()
        current = git_ops.repo.active_branch.name
        InteractiveUI.show_branches_table(branches, current)


@click.command()
@click.argument('name')
def switch(name):
    """Switch to a branch"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    git_ops.switch_branch(name)


@click.command()
@click.argument('branch')
def merge(branch):
    """Merge a branch"""
    git_ops = GitOperations()
    if not git_ops.is_git_repo():
        show_error("Not a git repository")
        return
    current = git_ops.repo.active_branch.name
    show_info(f"Merging {branch} into {current}...")
    try:
        git_ops.repo.git.merge(branch)
        show_success(f"Successfully merged {branch}")
    except Exception as e:
        show_error(f"Merge failed: {str(e)}")
        resolver = ConflictResolver(git_ops.repo)
        if resolver.has_conflicts():
            resolver.resolve_interactive()
