"""
GitHub commands for gitpush.
"""

import os
import click
import questionary
from git import Repo
from git import InvalidGitRepositoryError

from gitpush.core.github_manager import GitHubManager
from gitpush.ui.banner import show_progress, show_error, show_info, show_success, show_warning


@click.command()
@click.argument("repo_name", required=True)
@click.option("--description", "-d", help="Repository description")
@click.option("--private", is_flag=True, help="Make repository private")
@click.option("--public", is_flag=True, help="Make repository public (default)")
@click.option("--gitignore", "-g", help="Gitignore template (e.g., Python, Node)")
@click.option("--license", "-l", help="License (MIT, Apache-2.0, GPL-3.0)")
@click.option("--no-readme", is_flag=True, help="Skip README creation")
@click.option("--quick", is_flag=True, help="Use smart defaults, no prompts")
def new(repo_name, description, private, public, gitignore, license, no_readme, quick):
    """Create a new GitHub repository"""
    gh = GitHubManager()

    if not gh.authenticate():
        return

    try:
        repo = Repo(".")
        show_error("This directory is already a git repository!")
        show_info(f"Remote: {repo.remotes.origin.url if repo.remotes else 'None'}")
        return
    except InvalidGitRepositoryError:
        pass

    config = {"name": repo_name}

    if quick:
        show_info("Using smart defaults...")
        config["description"] = description or "Created with run-git"
        config["private"] = False
        config["gitignore"] = gh.detect_language()
        config["license"] = "mit"
        config["readme"] = True
    else:
        if not description:
            description = questionary.text("Repository description:", default="").ask()
        config["description"] = description

        if not private and not public:
            visibility = questionary.select(
                "Repository visibility:", choices=["Public", "Private"]
            ).ask()
            config["private"] = visibility == "Private"
        else:
            config["private"] = private

        if not gitignore:
            detected = gh.detect_language()
            use_detected = questionary.confirm(f"Use {detected} gitignore template?").ask()
            config["gitignore"] = detected if use_detected else None
        else:
            config["gitignore"] = gitignore

        if not license:
            licenses = gh.get_license_templates()
            license_choice = questionary.select(
                "Select license:", choices=list(licenses.keys())
            ).ask()
            config["license"] = licenses[license_choice]
        else:
            config["license"] = license.lower()

        config["readme"] = not no_readme
        if not no_readme:
            config["readme"] = questionary.confirm("Create README.md?").ask()

    github_repo = gh.create_repository(config)
    if not github_repo:
        return

    show_progress("Initializing local repository...")
    local_repo = Repo.init(".")

    if config.get("gitignore"):
        show_progress("Creating .gitignore...")
        content = gh.get_gitignore_content(config["gitignore"])
        if content:
            with open(".gitignore", "w") as f:
                f.write(content)

    if config.get("license"):
        show_progress("Creating LICENSE...")
        user = gh.github.get_user()
        content = gh.get_license_content(config["license"], user.name or user.login)
        if content:
            with open("LICENSE", "w") as f:
                f.write(content)

    if config.get("readme"):
        show_progress("Creating README.md...")
        user = gh.github.get_user()
        content = f"# {config['name']}\n\n{config.get('description', '')}\n"
        with open("README.md", "w") as f:
            f.write(content)

    show_progress("Adding remote origin...")
    local_repo.create_remote("origin", github_repo.clone_url)

    show_progress("Creating initial commit...")
    local_repo.git.add(A=True)
    local_repo.index.commit("Initial commit")
    local_repo.git.branch("-M", "main")

    show_progress("Pushing to GitHub...")
    origin = local_repo.remote("origin")
    try:
        origin.push("main")
    except Exception:
        show_warning("Push failed. Attempting to sync...")
        try:
            local_repo.git.pull("origin", "main", "--allow-unrelated-histories")
            origin.push("main")
        except Exception as e:
            show_error(f"Push failed: {str(e)}")
            return

    show_success("Repository created successfully!")
    show_info(f"Link: {github_repo.html_url}")
