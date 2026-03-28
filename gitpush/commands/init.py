"""
Init command for gitpush.
"""
import click
from git import Repo

from gitpush.core.git_operations import GitOperations
from gitpush.ui.banner import show_info, show_error, show_success
from gitpush.ui.interactive import InteractiveUI


@click.command()
@click.argument('url', required=False)
def init_command(url):
    """Initialize git repository"""
    git_ops = GitOperations()
    
    if url:
        show_info(f"Cloning repository from {url}...")
        try:
            Repo.clone_from(url, '.')
            show_success("Repository cloned successfully")
        except Exception as e:
            show_error(f"Failed to clone: {str(e)}")
    else:
        git_ops.init_repo()
        ui = InteractiveUI()
        if ui.confirm_action("Add remote repository?"):
            remote_url = ui.get_repo_url()
            git_ops.add_remote("origin", remote_url)
