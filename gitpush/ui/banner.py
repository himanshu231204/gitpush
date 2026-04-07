"""
Banner and UI elements for run-git
"""

import sys
import time
import threading
from rich.console import Console
from rich.theme import Theme
from rich.style import Style
from rich import box
from rich.text import Text
from rich.panel import Panel
from gitpush import __version__

# Custom theme
custom_theme = Theme(
    {
        "success": "bold green",
        "error": "bold red",
        "warning": "bold yellow",
        "info": "bold cyan",
        "accent": "bold magenta",
        "dim": "dim",
    }
)

console = Console(theme=custom_theme, legacy_windows=False, emoji=False)


# ══════════════════════════════════════════════════════════════════════════════
# DESIGN TOKENS SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

class DesignTokens:
    """Unified design tokens for consistent UI across the application."""
    
    # Spacing
    SPACING = {
        "tight": 0,
        "small": 1,
        "medium": 2,
        "large": 3,
        "xlarge": 4,
    }
    
    # Typography
    TYPOGRAPHY = {
        "heading": "bold",
        "body": "normal",
        "dim": "dim",
        "code": "italic",
    }
    
    # UI Elements
    ICONS = {
        "success": "✓",
        "error": "✗",
        "warning": "⚠",
        "info": "ℹ",
        "arrow": "→",
        "pointer": "►",
        "back": "←",
    }
    
    # Panel defaults
    PANEL = {
        "box": box.ROUNDED,
        "padding": (0, 1),
        "border_padding": (0, 0),
    }
    
    # Animation speeds
    ANIMATION = {
        "fast": 0.1,
        "normal": 0.25,
        "slow": 0.5,
    }


# Global design tokens instance
tokens = DesignTokens()


class ThemeManager:
    """Manage CLI color themes"""

    THEMES = {
        "default": {
            "primary": "cyan",
            "secondary": "green",
            "accent": "magenta",
            "success": "green",
            "error": "red",
            "warning": "yellow",
            "dim": "dim",
            "white": "white",
        },
        "dark": {
            "primary": "bright_cyan",
            "secondary": "bright_green",
            "accent": "bright_magenta",
            "success": "bright_green",
            "error": "bright_red",
            "warning": "bright_yellow",
            "dim": "dim",
            "white": "white",
        },
        "light": {
            "primary": "blue",
            "secondary": "green",
            "accent": "purple",
            "success": "green",
            "error": "red",
            "warning": "yellow",
            "dim": "dim",
            "black": "black",
        },
    }

    def __init__(self, theme_name="default"):
        self.theme_name = theme_name
        self.colors = self.THEMES.get(theme_name, self.THEMES["default"])
        
        # Add design tokens reference
        self.tokens = tokens
    
    def get(self, key):
        return self.colors.get(key, "cyan")
    
    def style_success(self, text):
        """Return styled success text."""
        return f"[{self.colors['success']}]{text}[/{self.colors['success']}]"
    
    def style_error(self, text):
        """Return styled error text."""
        return f"[{self.colors['error']}]{text}[/{self.colors['error']}]"
    
    def style_warning(self, text):
        """Return styled warning text."""
        return f"[{self.colors['warning']}]{text}[/{self.colors['warning']}]"
    
    def style_primary(self, text):
        """Return styled primary text."""
        return f"[{self.colors['primary']}]{text}[/{self.colors['primary']}]"


def set_theme(theme_name):
    """Set the color theme"""
    global current_theme
    current_theme = ThemeManager(theme_name)

    # Persist theme to config
    try:
        from gitpush.config import get_settings
        settings = get_settings()
        settings.set("theme", theme_name)
        settings.save()
    except Exception:
        pass  # Config may not be available yet

    # Refresh interactive UI styles
    try:
        from gitpush.ui.interactive import refresh_styles
        refresh_styles()
    except Exception:
        pass


def _load_saved_theme():
    """Load saved theme from config on startup"""
    try:
        from gitpush.config import get_settings
        saved_theme = get_settings().get("theme", "default")
        return ThemeManager(saved_theme)
    except Exception:
        return ThemeManager("default")


# Initialize with saved theme (if available)
current_theme = _load_saved_theme()


# Git Logo
GIT_LOGO = """
██████╗ ██╗   ██╗███╗   ██╗      ██████╗ ██╗████████╗
██╔══██╗██║   ██║████╗  ██║     ██╔════╝ ██║╚══██╔══╝
██████╔╝██║   ██║██╔██╗ ██║     ██║  ███╗██║   ██║   
██╔══██╗██║   ██║██║╚██╗██║     ██║   ██║██║   ██║   
██║  ██║╚██████╔╝██║ ╚████║     ╚██████╔╝██║   ██║   
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝      ╚═════╝ ╚═╝   ╚═╝   
"""

# Tagline
TAGLINE = "One Command • Zero Hassle • Full Control"


def get_banner(version=None):
    """Get simple banner (no animation)"""
    ver = version or __version__
    return f"""
{GIT_LOGO}
        [bold cyan]⚡ RUN-GIT ⚡[/bold cyan]
   [bold]Git Operations, Simplified[/bold]

 [dim]{TAGLINE}[/dim]
"""


def show_banner():
    """Display the run-git banner - simple version (no repeat)"""
    primary = current_theme.colors["primary"]
    console.print(f"[bold {primary}]{GIT_LOGO}[/bold {primary}]")
    console.print(f"\n        [bold {primary}]⚡ RUN-GIT ⚡[/bold {primary}]")
    console.print(f"   [bold]Git Operations, Simplified[/bold]\n")
    console.print(f" [dim]{TAGLINE}[/dim]")


def show_banner_with_version():
    """Display banner with version info"""
    primary = current_theme.colors["primary"]
    console.print(f"[bold {primary}]{GIT_LOGO}[/bold {primary}]")
    console.print(f"\n        [bold {primary}]⚡ RUN-GIT ⚡[/bold {primary}]")
    console.print(f"   [bold]Git Operations, Simplified[/bold]\n")
    console.print(f" [dim]{TAGLINE}[/dim]\n")
    console.print(f" [dim]v{__version__}[/dim]")


def show_success(message):
    """Show success message"""
    console.print(f"[OK]  {message}", style=f"bold {current_theme.colors['success']}")


def show_error(message):
    """Show error message with rich styling"""
    console.print(f"[X]  {message}", style=f"bold {current_theme.colors['error']}")


def show_error_panel(title, message, suggestion=None):
    """Show error in a rich panel with optional suggestion."""
    from rich.panel import Panel
    from rich.text import Text
    
    error = current_theme.colors["error"]
    primary = current_theme.colors["primary"]
    
    # Build content
    content = f"[bold {error}]{message}[/bold {error}]"
    if suggestion:
        content += f"\n\n[dim]Tip: {suggestion}[/dim]"
    
    panel = Panel(
        content,
        title=f"[bold {error}]✗ {title}[/bold {error}]",
        border_style=error,
        box=box.ROUNDED,
    )
    console.print(panel)


def show_warning(message):
    """Show warning message"""
    console.print(f"[!]  {message}", style=f"bold {current_theme.colors['warning']}")


def show_warning_panel(title, message, suggestion=None):
    """Show warning in a rich panel with optional suggestion."""
    from rich.panel import Panel
    
    warning = current_theme.colors["warning"]
    
    # Build content
    content = f"[bold {warning}]{message}[/bold {warning}]"
    if suggestion:
        content += f"\n\n[dim]Tip: {suggestion}[/dim]"
    
    panel = Panel(
        content,
        title=f"[bold {warning}]⚠ {title}[/bold {warning}]",
        border_style=warning,
        box=box.ROUNDED,
    )
    console.print(panel)
    """Show warning message"""
    console.print(f"[!]  {message}", style=f"bold {current_theme.colors['warning']}")


def show_info(message):
    """Show info message"""
    console.print(f"[i]  {message}", style=f"bold {current_theme.colors['primary']}")


def show_progress(message):
    """Show progress message"""
    console.print(f"[*] {message}", style=f"bold {current_theme.colors['accent']}")


def show_step(step, total, message):
    """Show progress step (e.g., 2/4)"""
    console.print(
        f"[{current_theme.colors['primary']}][{step}/{total}][/{current_theme.colors['primary']}] {message}"
    )


def show_keyhint(keys):
    """Show keyboard shortcuts hint"""
    hints = " | ".join([f"[bold]{k}[/]: {v}" for k, v in keys])
    console.print(f"[{current_theme.colors['dim']}]{hints}[/{current_theme.colors['dim']}]")


# Loading spinner for operations
class Spinner:
    """Animated spinner for long operations"""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message="Loading"):
        self.message = message
        self.frame = 0
        self.running = False

    def __enter__(self):
        self.running = True
        return self

    def __exit__(self, *args):
        self.running = False
        console.print("")

    def update(self, message=None):
        """Update spinner frame"""
        if message:
            self.message = message
        frame = self.FRAMES[self.frame % len(self.FRAMES)]
        print(f"\r{frame} {self.message}", end="", flush=True)
        self.frame += 1


def loading_spinner(func):
    """Decorator for spinner on functions"""

    def wrapper(*args, **kwargs):
        with Spinner("Processing..."):
            return func(*args, **kwargs)

    return wrapper


# Colorized git status
def colorize_status(status):
    """Return colorized status text"""
    colors = {
        "added": current_theme.colors["success"],
        "modified": current_theme.colors["warning"],
        "deleted": current_theme.colors["error"],
        "untracked": current_theme.colors["primary"],
        "renamed": current_theme.colors["accent"],
    }

    def colorize(text, status_type):
        color = colors.get(status_type, "white")
        return f"[{color}]{text}[/{color}]"

    return colorize


# Command suggestion
def show_suggestion(command, explanation):
    """Show command suggestion"""
    primary = current_theme.colors["primary"]
    console.print(f"→ Did you mean: [bold {primary}]{command}[/]? {explanation}")


# Keyboard shortcut display
KEYBOARD_SHORTCUTS = {
    "?": "Show help",
    "h": "Help menu",
    "q": "Quit",
    "r": "Refresh",
    "p": "Quick push",
    "s": "Status",
    "g": "Commit graph",
    "b": "Branch menu",
    "c": "Cancel",
    "enter": "Confirm",
    "esc": "Go back",
}


def show_shortcuts():
    """Show available keyboard shortcuts"""
    from rich.table import Table
    from rich.panel import Panel

    table = Table(show_header=True, header_style=f"bold {current_theme.colors['primary']}")
    table.add_column("Key", style="yellow", width=8)
    table.add_column("Action", style="white")

    for key, action in KEYBOARD_SHORTCUTS.items():
        table.add_row(f"[bold]{key}[/]", action)

    panel = Panel(
        table,
        title=f"[{current_theme.colors['primary']}]⌨  Keyboard Shortcuts[/{current_theme.colors['primary']}]",
        border_style=current_theme.colors["primary"],
        box=box.ROUNDED,
    )
    console.print(panel)


def clear_screen():
    """Clear the terminal screen"""
    console.clear()
