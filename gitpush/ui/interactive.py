"""
Interactive UI components for gitpush
"""

import questionary
from questionary import Style as QStyle
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich import box
from rich.style import Style
from rich.rule import Rule
from gitpush.ui.banner import current_theme, show_shortcuts, show_success, show_error, show_info
from gitpush.core.git_operations import GitOperations
from gitpush.core.ai_engine import AIEngine
from gitpush.config.settings import get_settings
from gitpush.ai.config import AIConfig

console = Console()

# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC QUESTIONARY STYLES (Theme-aware)
# ══════════════════════════════════════════════════════════════════════════════

def get_menu_style(menu_type="main"):
    """Get questionary style based on current theme and menu type."""
    from gitpush.ui.banner import current_theme
    
    primary = current_theme.colors["primary"]
    secondary = current_theme.colors["secondary"]
    accent = current_theme.colors["accent"]
    warning = current_theme.colors["warning"]
    
    # Map menu types to colors
    color_map = {
        "main": primary,
        "branch": secondary,
        "ai": accent,
        "advanced": warning,
        "settings": primary,
        "graph": primary,
        "confirm": secondary,
        "input": primary,
    }
    
    color = color_map.get(menu_type, primary)
    
    return QStyle(
        [
            ("qmark", f"fg:{color} bold"),
            ("pointer", f"fg:{color} bold"),
            ("highlighted", f"fg:{color} bold"),
            ("selected", f"fg:{color} bold"),
        ]
    )


# Legacy style references (for backward compatibility)
# These will be set dynamically when used
MAIN_MENU_STYLE = get_menu_style("main")
BRANCH_MENU_STYLE = get_menu_style("branch")
AI_MENU_STYLE = get_menu_style("ai")
ADVANCED_MENU_STYLE = get_menu_style("advanced")
SETTINGS_MENU_STYLE = get_menu_style("settings")
GRAPH_MENU_STYLE = get_menu_style("graph")
CONFIRM_STYLE = get_menu_style("confirm")
INPUT_STYLE = get_menu_style("input")


def refresh_styles():
    """Refresh all menu styles to match current theme."""
    global MAIN_MENU_STYLE, BRANCH_MENU_STYLE, AI_MENU_STYLE
    global ADVANCED_MENU_STYLE, SETTINGS_MENU_STYLE, GRAPH_MENU_STYLE
    global CONFIRM_STYLE, INPUT_STYLE
    
    MAIN_MENU_STYLE = get_menu_style("main")
    BRANCH_MENU_STYLE = get_menu_style("branch")
    AI_MENU_STYLE = get_menu_style("ai")
    ADVANCED_MENU_STYLE = get_menu_style("advanced")
    SETTINGS_MENU_STYLE = get_menu_style("settings")
    GRAPH_MENU_STYLE = get_menu_style("graph")
    CONFIRM_STYLE = get_menu_style("confirm")
    INPUT_STYLE = get_menu_style("input")


# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM MENU SYSTEM
# ══════════════════════════════════════════════════════════════════════════════


def show_repo_context():
    """Display repository context info at the top of the menu"""
    from gitpush.core.git_operations import GitOperations

    git_ops = GitOperations()

    if not git_ops.is_git_repo():
        # Show "Not a git repo" message
        error_color = current_theme.colors["error"]
        panel = Panel(
            f"[bold {error_color}]⚠ Not a Git Repository[/bold {error_color}]\n"
            "[dim]Run 'run-git init' to initialize or navigate to a git repo[/dim]",
            title="[bold]📁 CONTEXT[/bold]",
            border_style=error_color,
            box=box.ROUNDED,
        )
        console.print(panel)
        return None

    # Get repo info
    repo_name = git_ops.repo.working_dir.split("/")[-1] if git_ops.repo.working_dir else "Unknown"
    branch_name = git_ops.repo.active_branch.name if git_ops.repo.active_branch else "main"
    status_data = git_ops.get_status()

    # Calculate status
    total_changes = (
        len(status_data.get("staged", []))
        + len(status_data.get("modified", []))
        + len(status_data.get("untracked", []))
        + len(status_data.get("deleted", []))
    )

    if total_changes == 0:
        status_text = "[green]✓ Clean[/green]"
    else:
        status_text = f"[yellow]● {total_changes} change(s)[/yellow]"

    # Build context info
    primary = current_theme.colors["primary"]
    secondary = current_theme.colors["secondary"]
    accent = current_theme.colors["accent"]
    context_info = (
        f"[bold {primary}]Repo:[/bold {primary}] {repo_name}\n"
        f"[bold {secondary}]Branch:[/bold {secondary}] {branch_name}\n"
        f"[bold {accent}]Status:[/bold {accent}] {status_text}"
    )

    panel = Panel(
        context_info,
        title="[bold]📁 CONTEXT[/bold]",
        border_style=primary,
        box=box.ROUNDED,
    )
    console.print(panel)


# ══════════════════════════════════════════════════════════════════════════════
# VIM-ENABLED MENU SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

class VimSelect:
    """Custom select with vim keybindings (j/k for navigation, Enter to select)."""
    
    def __init__(self, choices, choice_map, style, title="", qmark="▶", pointer="►"):
        self.choices = choices
        self.choice_map = choice_map
        self.style = style
        self.title = title
        self.qmark = qmark
        self.pointer = pointer
        self.selected_index = 0
    
    def run(self):
        """Run the vim-enabled selection."""
        from gitpush.ui.banner import current_theme
        
        primary = current_theme.colors["primary"]
        
        while True:
            # Display menu with current selection highlighted
            self._display()
            
            # Get input
            try:
                key = self._get_key()
                
                if key == "j" or key == "down":
                    self.selected_index = min(self.selected_index + 1, len(self.choices) - 1)
                elif key == "k" or key == "up":
                    self.selected_index = max(self.selected_index - 1, 0)
                elif key == "g":
                    self.selected_index = 0
                elif key == "G":
                    self.selected_index = len(self.choices) - 1
                elif key == "\r" or key == "\n":  # Enter
                    return self._get_selection()
                elif key == "b":
                    return "back"
                elif key == "q":
                    return "quit"
                elif key == "?":
                    self._show_help()
                else:
                    pass  # Ignore other keys
                    
            except (KeyboardInterrupt, EOFError):
                return ""
    
    def _display(self):
        """Display the menu."""
        console.print("\n")
        for idx, choice in enumerate(self.choices):
            if idx == self.selected_index:
                console.print(f"  {self.pointer} {choice}")
            else:
                console.print(f"     {choice}")
        console.print()
    
    def _get_key(self):
        """Get a single key press."""
        import tty
        import termios
        import sys
        
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            return sys.stdin.read(1)
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def _get_selection(self):
        """Get the selected choice."""
        if 0 <= self.selected_index < len(self.choices):
            selected = self.choices[self.selected_index]
            return self.choice_map.get(selected, "")
        return ""
    
    def _show_help(self):
        """Show help overlay."""
        from gitpush.ui.banner import current_theme
        from rich.panel import Panel
        
        primary = current_theme.colors["primary"]
        help_text = """
[bold]Keyboard Shortcuts[/bold]

[bold {primary}]j/k or ↑/↓[/{primary}]   Navigate menu
[bold {primary}]g[/{primary}]              Go to first item
[bold {primary}]G[/{primary}]              Go to last item
[bold {primary}]Enter[/{primary}]          Select item
[bold {primary}]b[/{primary}]              Go back
[bold {primary}]q[/{primary}]              Quit
[bold {primary}]?[/{primary}]              Show this help
        """.format(primary=primary)
        
        panel = Panel(help_text, title="[bold]⌨  Help[/bold]", border_style=primary, box=box.ROUNDED)
        console.print(panel)


def vim_select(choices, choice_map, style, title="", qmark="▶", pointer="►"):
    """Wrapper function for vim-enabled selection."""
    selector = VimSelect(choices, choice_map, style, title, qmark, pointer)
    return selector.run()


# ══════════════════════════════════════════════════════════════════════════════
# SMART HELP SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

# Global shortcut hints that can be shown in menus
MENU_SHORTCUTS = {
    "main_menu": [
        ("p", "Push changes"),
        ("s", "Switch branch"),
        ("c", "Commit with AI"),
        ("b", "Branch menu"),
        ("a", "AI features"),
        ("?", "Show help"),
    ],
    "branch_menu": [
        ("c", "Create branch"),
        ("s", "Switch branch"),
        ("l", "List branches"),
        ("d", "Delete branch"),
        ("m", "Merge branch"),
    ],
    "ai_menu": [
        ("c", "AI Commit"),
        ("p", "AI PR"),
        ("r", "AI Review"),
        ("s", "Settings"),
    ],
}


def show_context_hints(menu_type="main_menu"):
    """Show context-aware keyboard hints."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    from gitpush.ui.banner import current_theme
    
    primary = current_theme.colors["primary"]
    secondary = current_theme.colors["secondary"]
    
    shortcuts = MENU_SHORTCUTS.get(menu_type, [])
    
    if not shortcuts:
        return
    
    # Build hint text
    hint_lines = []
    for key, action in shortcuts:
        hint_lines.append(f"[bold {primary}]{key}[/bold {primary}]  {action}")
    
    hint_text = "  |  ".join(hint_lines)
    
    # Show as inline hint
    console.print(f"\n[dim]Hint: {hint_text}[/dim]\n")


# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM MENU SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
    # ENHANCED TABLE DISPLAYS WITH ZEBRA STRIPING
    # ══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def show_status_dashboard(status):
        """Display comprehensive git status dashboard with zebra-striped table"""
        # Summary panel with key stats
        untracked_count = len(status.get("untracked", []))
        modified_count = len(status.get("modified", []))
        staged_count = len(status.get("staged", []))
        deleted_count = len(status.get("deleted", []))

        # Create a summary stats row
        primary = current_theme.colors["primary"]
        secondary = current_theme.colors["secondary"]
        warning = current_theme.colors["warning"]
        error = current_theme.colors["error"]
        stats_panel = Panel(
            f"[bold {primary}]Branch:[/bold {primary}] {status.get('branch', 'N/A')}\n"
            f"[bold {secondary}]✓ Staged:[/bold {secondary}] {staged_count}  |  "
            f"[bold {warning}]✏️  Modified:[/bold {warning}] {modified_count}  |  "
            f"[bold {error}]🗑️  Deleted:[/bold {error}] {deleted_count}  |  "
            f"[bold {primary}]🆕 Untracked:[/bold {primary}] {untracked_count}",
            title="[bold]📊 REPOSITORY STATUS[/bold]",
            border_style=current_theme.colors["primary"],
            box=box.ROUNDED,
        )
        console.print(stats_panel)

        # Zebra-striped table for changes
        table = Table(
            show_header=True,
            header_style=f"bold {current_theme.colors['primary']}",
            border_style=current_theme.colors["primary"],
            box=box.ROUNDED,
            pad_edge=False,
            expand=True,
        )
        primary = current_theme.colors["primary"]
        table.add_column("Status", style=primary, width=12)
        table.add_column("Files", style="white", justify="left")

        # Zebra striping with alternating styles
        for idx, (category, files, icon, color) in enumerate(
            [
                ("✅ Staged", status.get("staged", []), "A", "green"),
                ("✏️  Modified", status.get("modified", []), "M", "yellow"),
                ("🗑️  Deleted", status.get("deleted", []), "D", "red"),
                ("🆕 Untracked", status.get("untracked", []), "?", "blue"),
            ]
        ):
            if files:
                # Alternating row style
                row_style = "dim" if idx % 2 == 0 else ""
                file_list = "\n".join([f"  [{color}]{icon}[/{color}]  {f}" for f in files[:10]])
                if len(files) > 10:
                    file_list += f"\n  ... and {len(files) - 10} more"
                # Only apply style tags when row_style is not empty
                if row_style:
                    table.add_row(
                        f"[{row_style}]{category}[/{row_style}]",
                        f"[{row_style}]{file_list}[/{row_style}]",
                    )
                else:
                    table.add_row(category, file_list)

        console.print(table)

        # Show detailed file lists for each category
        for category, files, icon, color in [
            ("Staged", status.get("staged", []), "A", "green"),
            ("Modified", status.get("modified", []), "M", "yellow"),
            ("Deleted", status.get("deleted", []), "D", "red"),
            ("Untracked", status.get("untracked", []), "?", "blue"),
        ]:
            if files:
                console.print(f"\n[bold {color}]📁 {category} files:[/bold {color}]")
                for f in files:
                    console.print(f"   [{color}]{icon}[/{color}]  {f}")

    @staticmethod
    def show_status_table(status):
        """Display status in enhanced table (legacy compatibility)"""
        InteractiveUI.show_status_dashboard(status)

    @staticmethod
    def show_log_table(commits):
        """Display commit log in zebra-striped table"""
        table = Table(
            title="📜 Recent Commits",
            show_header=True,
            header_style=f"bold {current_theme.colors['primary']}",
            border_style=current_theme.colors["primary"],
            box=box.ROUNDED,
            pad_edge=False,
        )
        table.add_column("🏷️  Hash", style=f"{current_theme.colors['warning']}", width=8)
        table.add_column("👤 Author", style=f"{current_theme.colors['primary']}", width=15)
        table.add_column("📅 Date", style=f"{current_theme.colors['success']}", width=12)
        table.add_column("💬 Message", style="white")

        for idx, commit in enumerate(commits):
            msg = commit.get("message", "")
            truncated = msg[:50] + "..." if len(msg) > 50 else msg
            # Zebra striping - alternate between dim and normal
            row_style = "dim" if idx % 2 == 0 else ""

            # Only apply style when row_style is not empty
            if row_style:
                table.add_row(
                    f"[{row_style}][yellow]{commit.get('hash', '')[:7]}[/yellow][/{row_style}]",
                    f"[{row_style}]{commit.get('author', 'Unknown')[:15]}[/{row_style}]",
                    f"[{row_style}]{commit.get('date', '')[:10]}[/{row_style}]",
                    f"[{row_style}]{truncated}[/{row_style}]",
                )
            else:
                table.add_row(
                    f"[yellow]{commit.get('hash', '')[:7]}[/yellow]",
                    commit.get("author", "Unknown")[:15],
                    commit.get("date", "")[:10],
                    truncated,
                )

        console.print()
        console.print(table)

    @staticmethod
    def show_branches_table(branches, current_branch):
        """Display branches in zebra-striped table"""
        table = Table(
            title="🌿 Branches",
            show_header=True,
            header_style=f"bold {current_theme.colors['primary']}",
            border_style=current_theme.colors["primary"],
            box=box.ROUNDED,
            pad_edge=False,
        )
        table.add_column("🌿 Branch", style="white")
        table.add_column("📍 Status", style=f"{current_theme.colors['success']}", justify="center")

        for idx, branch in enumerate(branches):
            is_current = branch == current_branch
            status = "✓ Current" if is_current else ""
            # Zebra striping
            row_style = "dim" if idx % 2 == 0 else ""

            if row_style:
                if is_current:
                    table.add_row(
                        f"[{row_style}][bold {current_theme.colors['success']}]► {branch}[/bold {current_theme.colors['success']}][/{row_style}]",
                        f"[{row_style}][bold {current_theme.colors['success']}]{status}[/bold {current_theme.colors['success']}][/{row_style}]",
                    )
                else:
                    table.add_row(
                        f"[{row_style}]  {branch}[/{row_style}]",
                        f"[{row_style}]{status}[/{row_style}]",
                    )
            else:
                if is_current:
                    table.add_row(
                        f"[bold {current_theme.colors['success']}]► {branch}[/bold {current_theme.colors['success']}]",
                        f"[bold {current_theme.colors['success']}]{status}[/bold {current_theme.colors['success']}]",
                    )
                else:
                    table.add_row(f"  {branch}", status)

        console.print()
        console.print(table)

    @staticmethod
    def show_remotes_table(git_ops):
        """Display remotes in a styled table"""
        remotes = list(git_ops.repo.remotes)

        if not remotes:
            show_info("No remotes configured")
            return

        primary = current_theme.colors["primary"]
        table = Table(
            title="🔗 Remote Repositories",
            show_header=True,
            header_style=f"bold {primary}",
            border_style=primary,
            box=box.ROUNDED,
        )
        table.add_column("Name", style=primary, width=15)
        table.add_column("URL", style="white")

        for idx, remote in enumerate(remotes):
            row_style = "dim" if idx % 2 == 0 else ""

            if row_style:
                table.add_row(
                    f"[{row_style}][bold {primary}]{remote.name}[/bold {primary}][/{row_style}]",
                    f"[{row_style}]{remote.url}[/{row_style}]",
                )
            else:
                table.add_row(
                    f"[bold {primary}]{remote.name}[/bold {primary}]",
                    remote.url,
                )

        console.print(table)

    @staticmethod
    def show_tags_table(git_ops):
        """Display tags in a styled table"""
        tags = list(git_ops.repo.tags)

        if not tags:
            show_info("No tags found")
            return

        primary = current_theme.colors["primary"]
        warning = current_theme.colors["warning"]
        table = Table(
            title="🏷️  Tags",
            show_header=True,
            header_style=f"bold {primary}",
            border_style=primary,
            box=box.ROUNDED,
        )
        table.add_column("Tag Name", style=warning, width=30)
        table.add_column("Commit", style="white", width=12)

        for idx, tag in enumerate(tags):
            row_style = "dim" if idx % 2 == 0 else ""
            commit_sha = tag.commit.hexsha[:7] if hasattr(tag, "commit") else "N/A"

            if row_style:
                table.add_row(
                    f"[{row_style}][bold {warning}]{tag.name}[/bold {warning}][/{row_style}]",
                    f"[{row_style}]{commit_sha}[/{row_style}]",
                )
            else:
                table.add_row(
                    f"[bold {warning}]{tag.name}[/bold {warning}]",
                    commit_sha,
                )

        console.print(table)

    # ══════════════════════════════════════════════════════════════════════════════
    # PROGRESS BAR UTILITIES
    # ══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def show_operation_progress(description="Processing..."):
        """Create an enhanced progress bar for operations with timing"""
        progress = Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=40, complete_style="cyan", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        )
        progress.__enter__()
        return progress

    @staticmethod
    def show_progress_bar(description="Processing..."):
        """Create a progress bar for long operations (legacy)"""
        progress = Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            console=console,
        )
        return progress


# Command suggestions based on common mistakes
COMMAND_SUGGESTIONS = {
    "git push": "run-git push",
    "git commit": "run-git push (includes commit)",
    "git status": "run-git status",
    "git log": "run-git log",
    "git branch": "run-git branch",
    "git checkout": "run-git switch",
    "git pull": "run-git pull",
    "git clone": "run-git init",
}


def suggest_command(misspelled):
    """Suggest correct command"""
    from gitpush.ui.banner import show_suggestion

    for wrong, correct in COMMAND_SUGGESTIONS.items():
        if wrong in misspelled.lower():
            show_suggestion(correct, "is the run-git equivalent")
            return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
# INTERACTIVE UI CLASS - Wrapper for backwards compatibility
# ══════════════════════════════════════════════════════════════════════════════


class InteractiveUI:
    """Wrapper class for interactive UI functions (backwards compatibility)."""

    @staticmethod
    def show_status_table(status):
        """Display status in table format."""
        from gitpush.ui.interactive import show_status_dashboard
        show_status_dashboard(status)

    @staticmethod
    def show_branches_table(branches, current_branch):
        """Display branches in table format."""
        # Create a simple table display
        from rich.console import Console
        from rich.table import Table
        from gitpush.ui.banner import current_theme
        
        console = Console()
        table = Table(title="Branches", show_header=True)
        table.add_column("Branch", style="white")
        table.add_column("Status", style="green")
        
        for branch in branches:
            is_current = branch == current_branch
            status = "Current" if is_current else ""
            table.add_row(branch, status)
        
        console.print(table)

    @staticmethod
    def show_log_table(commits):
        """Display commit log in table format."""
        from rich.console import Console
        from rich.table import Table
        from gitpush.ui.banner import current_theme
        
        console = Console()
        table = Table(title="Recent Commits", show_header=True)
        table.add_column("Hash", style="yellow", width=8)
        table.add_column("Author", style="white", width=15)
        table.add_column("Message", style="white")
        
        for commit in commits:
            table.add_row(
                commit.get("hash", "")[:7],
                commit.get("author", "Unknown")[:15],
                commit.get("message", "")[:50]
            )
        
        console.print(table)

    @staticmethod
    def confirm_action(message):
        """Ask for user confirmation."""
        import questionary
        return questionary.confirm(message).ask()

    @staticmethod
    def ai_menu():
        """Show AI menu."""
        # Import and call the main menu
        from gitpush.ui.interactive import main_menu
        main_menu()
