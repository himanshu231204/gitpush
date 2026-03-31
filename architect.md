# Architecture of `run-git`

## Table of Contents

1. [Overview](#overview)
2. [Repository Structure](#repository-structure)
3. [Architectural Layers](#architectural-layers)
4. [Module Breakdown](#module-breakdown)
5. [Data Flow](#data-flow)
6. [Key Workflows](#key-workflows)
7. [Configuration & Storage](#configuration--storage)
8. [Technology Stack](#technology-stack)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Dependency Map](#dependency-map)

---

## Overview

`run-git` is a Python CLI tool that wraps common Git and GitHub operations into intuitive, single commands with smart defaults and automation. It is published to PyPI as the `run-git` package (version `1.4.0`) and installed globally as the `run-git` command.

**Primary goals:**
- Remove the need to memorise multiple Git subcommands for daily workflows.
- Auto-generate conventional commit messages based on the types of files changed.
- Provide an interactive terminal UI for users who prefer menu-driven operation.
- Integrate directly with the GitHub API for repository creation, branching, and remote management.
- AI-powered features: commit messages, code reviews, PR descriptions.

---

## Repository Structure

```
gitpush/                          ← repository root
├── .github/
│   └── workflows/
│       ├── tests.yml             ← pytest CI (Python 3.9 – 3.11)
│       ├── publish.yml           ← automated PyPI publish on release
│       └── quality.yml           ← black / flake8 / pylint quality gates
│
├── docs/
│   └── QUICKSTART.md             ← end-user quick-start guide
│
├── gitpush/                      ← installable Python package
│   ├── __init__.py               ← package version (1.4.0)
│   ├── __main__.py               ← `python -m gitpush` entry point
│   ├── cli.py                    ← Click CLI commands
│   ├── exceptions.py             ← custom exceptions
│   │
│   ├── commands/                 ← modular command handlers
│   │   ├── __init__.py
│   │   ├── push.py              ← push command
│   │   ├── init.py              ← init/clone command
│   │   ├── status.py            ← status command
│   │   ├── branch.py            ← branch operations
│   │   ├── remote.py            ← remote management
│   │   ├── stash.py             ← stash operations
│   │   ├── github.py            ← GitHub integration
│   │   ├── graph.py             ← commit graph visualization
│   │   └── undo.py              ← undo command
│   │
│   ├── core/                     ← business logic (no UI dependencies)
│   │   ├── __init__.py
│   │   ├── git_operations.py     ← GitPython wrapper
│   │   ├── commit_generator.py   ← Conventional Commits generator
│   │   ├── conflict_resolver.py  ← interactive merge conflict helper
│   │   └── github_manager.py     ← PyGithub / GitHub API integration
│   │
│   ├── ui/                       ← presentation layer
│   │   ├── __init__.py
│   │   ├── banner.py             ← Rich-formatted output helpers
│   │   └── interactive.py        ← Questionary-based prompts & tables
│   │
│   ├── utils/                    ← shared utilities
│   │   ├── __init__.py
│   │   ├── validators.py        ← input validation
│   │   ├── formatters.py         ← output formatting
│   │   └── file_helpers.py      ← file operations
│   │
│   ├── config/                   ← configuration
│   │   ├── __init__.py
│   │   └── settings.py          ← settings management
│   │
│   └── ai/                       ← AI features
│       ├── __init__.py
│       ├── provider.py          ← AI provider abstraction
│       └── prompts/             ← prompt templates
│
├── tests/
│   ├── __init__.py
│   ├── test_basic.py             ← 10 basic unit tests
│   └── test_comprehensive.py     ← 20+ comprehensive tests
│
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE                       ← MIT
├── setup.py
├── pyproject.toml                ← PEP 517 build config & entry-point
├── requirements.txt
└── pytest.ini
```

---

## Architectural Layers

The codebase follows a clean **four-tier layered architecture**:

```
┌──────────────────────────────────────────────┐
│         CLI Layer  (cli.py + commands/)      │
│  • Click command groups & option parsing     │
│  • Interactive TUI menu routing              │
│  • 15+ command handlers (in commands/)      │
└────────────────────┬─────────────────────────┘
                     │ calls
       ┌─────────────┴──────────────┐
       │                            │
┌──────▼────────────┐  ┌────────────▼────────────┐
│   Core Layer      │  │      UI Layer            │
├───────────────────┤  ├──────────────────────────┤
│ git_operations    │  │ banner.py                │
│ commit_generator  │  │ (Rich console output)    │
│ conflict_resolver │  │ interactive.py           │
│ github_manager    │  │ (Questionary prompts &   │
└───────────────────┘  │  Rich tables)            │
                       └──────────────────────────┘
│ github_manager    │  │ (Questionary prompts &   │
└───────────────────┘  │  Rich tables)            │
                       └──────────────────────────┘

┌──────────────────────────────────────────────┐
│            Config / Storage Layer            │
│  • ~/.run-git/config.yml  (GitHub token)     │
│  • gitpush/config/templates/  (gitignore)    │
└──────────────────────────────────────────────┘
```

| Layer | Responsibility | Key files |
|-------|---------------|-----------|
| **CLI** | Parse user input, route to handlers, compose workflows | `cli.py` |
| **Core** | Git / GitHub operations, business logic | `core/*.py` |
| **UI** | Display output, gather interactive input | `ui/*.py` |
| **Config** | Read/write persistent user configuration | `config/` |

---

## Module Breakdown

### `cli.py` — Command Entry Point

Registered as `run-git = gitpush.cli:main` via `pyproject.toml`.

- Uses Click's `@group(invoke_without_command=True)` to fall back to the interactive TUI when no subcommand is given.
- Delegates to modular command handlers in `commands/` directory.

### `commands/` — Modular Command Handlers

The `commands/` directory contains isolated command modules for maintainability:

| Module | Command | Description |
|--------|---------|-------------|
| `push.py` | `run-git push` | Stage → commit (auto/custom) → pull → push |
| `init.py` | `run-git init` | Initialize local repo or clone from URL |
| `status.py` | `run-git status`, `run-git log` | Rich status table, commit history |
| `branch.py` | `run-git branch`, `run-git switch`, `run-git merge` | Branch operations |
| `remote.py` | `run-git remote` | Manage remote URLs |
| `stash.py` | `run-git stash` | Stash/pop changes |
| `github.py` | `run-git new` | Create GitHub repository |
| `graph.py` | `run-git graph` | Commit graph visualization |
| `undo.py` | `run-git undo` | Undo last commit |
| `config.py` | `run-git config` | Configuration management |

**Design principle**: Each command is isolated in its own module. CLI orchestration (`cli.py`) parses args, calls the appropriate command module, and renders output.

---

### `core/git_operations.py` — Git Wrapper

Thin, testable wrapper around **GitPython** (`git.Repo`).

```
GitOperations
├── is_git_repo()            → bool
├── init_repo(remote_url)    → Repo
├── add_remote(name, url)
├── get_status()             → { branch, untracked, modified, staged }
├── add_all()
├── commit(message)
├── pull(remote, branch)
├── push(remote, branch, force)
├── get_branches()           → [Branch]
├── create_branch(name)
├── switch_branch(name)
├── delete_branch(name, force)
├── get_log(max_count)       → [Commit]
└── check_sensitive_files()  → [str]   ← detects .env, secrets, tokens
```

---

### `core/commit_generator.py` — Auto Commit Messages

Implements the [Conventional Commits](https://www.conventionalcommits.org/) specification.

```
CommitGenerator
├── generate_message(custom_message) → str
├── _get_file_changes()              → status dict
├── _analyze_changes(status)         → (prefix, description)
└── _categorize_files(files)         → { code, docs, config, tests }
```

**File categorisation rules:**

| Category | Extensions / Patterns |
|----------|----------------------|
| Code | `.py` `.js` `.jsx` `.ts` `.tsx` `.java` `.cpp` `.c` `.go` `.rs` `.rb` `.php` |
| Docs | `.md` `.txt` `.rst` `.pdf` `.doc` `.docx` |
| Config | `.json` `.yaml` `.yml` `.toml` `.ini` `.cfg` `.conf` |
| Tests | files containing `test`, `spec`, or `__test__` |

**Example output:** `feat: add authentication module (3 files added)`

---

### `core/conflict_resolver.py` — Merge Conflict Helper

```
ConflictResolver
├── has_conflicts()          → bool
├── get_conflicted_files()   → [str]
├── show_conflict_info()     ← Rich table display
└── resolve_interactive()    ← menu: keep yours / keep theirs / manual / diff / abort
```

---

### `core/github_manager.py` — GitHub API Integration

Uses **PyGithub** to interact with the GitHub REST API.

```
GitHubManager
├── authenticate()                      → github.Github
├── create_repository(config)           → Repository
├── get_gitignore_templates()           → [str]
├── get_license_templates()             → [str]
├── repo_exists(name)                   → bool
├── suggest_repo_name(base)             → str
├── detect_language()                   → str | None
├── get_gitignore_content(template)     → str
└── get_license_content(license, author)→ str
```

---

### `ui/banner.py` — Formatted Output

Wraps **Rich** for consistent, color-coded terminal output:

| Function | Style | Icon |
|----------|-------|------|
| `show_banner()` | ASCII art header | |
| `show_success(msg)` | green | ✅ |
| `show_error(msg)` | red | ❌ |
| `show_warning(msg)` | yellow | ⚠️ |
| `show_info(msg)` | blue | ℹ️ |
| `show_progress(msg)` | magenta | ⏳ |

---

### `ui/interactive.py` — Interactive Prompts

Uses **Questionary** for menus and **Rich** for table display:

```
InteractiveUI
├── main_menu()               → str   (chosen action)
├── branch_menu()             → str
├── get_commit_message()      → str
├── get_repo_url()            → str
├── confirm_action(question)  → bool
├── show_status_table(status)
├── show_log_table(commits)
├── show_branches_table(branches, current)
└── select_branch(branches)   → str
```

---

## Data Flow

### `run-git push` (most common workflow)

```
User runs: run-git push [-m "msg"]
        │
        ▼
cli.py:push()
        │
        ├─► GitOperations.is_git_repo()       ← abort if not a repo
        ├─► GitOperations.get_status()        ← detect changes
        ├─► InteractiveUI.show_status_table() ← display to user
        ├─► GitOperations.check_sensitive_files() ← warn about secrets
        ├─► GitOperations.add_all()           ← git add .
        ├─► CommitGenerator.generate_message() ← auto or custom message
        ├─► GitOperations.commit(message)     ← git commit
        ├─► GitOperations.pull()              ← git pull (rebase)
        │       └─► ConflictResolver (if conflicts)
        └─► GitOperations.push()              ← git push
```

### `run-git new <name>` (GitHub repo creation)

```
User runs: run-git new my-project
        │
        ▼
cli.py:new()
        │
        ├─► GitHubManager.authenticate()
        ├─► InteractiveUI prompts (description, visibility, license, .gitignore)
        ├─► GitHubManager.create_repository(config)
        ├─► GitOperations.init_repo()
        ├─► Create: .gitignore, LICENSE, README.md  (from GitHub templates)
        ├─► GitOperations.add_all()
        ├─► GitOperations.commit("Initial commit")
        ├─► GitOperations.add_remote("origin", repo.clone_url)
        └─► GitOperations.push(branch="main")
```

---

## Configuration & Storage

All persistent state is stored in a single YAML file:

| Location | Contents |
|----------|----------|
| `~/.run-git/config.yml` | `github_token: ghp_...` |

The token is written once (via `run-git init` or the config menu) and read on every command that calls `GitHubManager.authenticate()`.

**Required GitHub token scopes:** `repo` (full control of private repos), `user` (read profile).

No database is used. All transient repository state (branches, commits, working tree) is read live via GitPython from the local `.git` directory.

---

## Technology Stack

| Concern | Library | Version |
|---------|---------|---------|
| CLI framework | [Click](https://click.palletsprojects.com/) | ≥ 8.0.0 |
| Terminal UI / tables | [Rich](https://rich.readthedocs.io/) | ≥ 13.0.0 |
| Git access | [GitPython](https://gitpython.readthedocs.io/) | ≥ 3.1.0 |
| GitHub API | [PyGithub](https://pygithub.readthedocs.io/) | ≥ 1.59.0 |
| Interactive prompts | [Questionary](https://questionary.readthedocs.io/) | ≥ 1.10.0 |
| Config files | [PyYAML](https://pyyaml.org/) | ≥ 6.0 |
| HTTP | [Requests](https://requests.readthedocs.io/) | ≥ 2.28.0 |
| Testing | [pytest](https://docs.pytest.org/) + pytest-cov | ≥ 7.0.0 |
| Formatting | [black](https://black.readthedocs.io/) | latest |
| Linting | flake8, pylint | latest |
| Build | setuptools + [build](https://build.pypa.io/) | — |

---

## CI/CD Pipeline

Three GitHub Actions workflows are defined in `.github/workflows/`:

### `tests.yml` — Automated Tests

```
Trigger: push → main / develop
         pull_request → main

Matrix: Python 3.9, 3.10, 3.11 on ubuntu-latest

Steps:
  1. Checkout code
  2. Set up Python (matrix version)
  3. pip install -e ".[dev]"
  4. pytest tests/ -v --cov=gitpush
```

### `quality.yml` — Code Quality Gates

```
Trigger: push → main / develop
         pull_request → main

Steps:
  1. black --check .          (formatting)
  2. flake8 --max-line-length 127 --max-complexity 10
  3. pylint gitpush/
```

### `publish.yml` — PyPI Release

```
Trigger: GitHub Release published  OR  workflow_dispatch

Steps:
  1. python -m build
  2. twine check dist/*
  3. twine upload dist/*       (uses PYPI_API_TOKEN secret)
```

---

## Dependency Map

```
run-git (cli.py)
    │
    ├── click                    ← @group, @command, @option decorators
    │
    ├── core/git_operations.py
    │       └── GitPython (git)  ← Repo, IndexFile, remote operations
    │
    ├── core/commit_generator.py
    │       └── GitPython (git)  ← diff / status introspection
    │
    ├── core/conflict_resolver.py
    │       └── GitPython (git)  ← unmerged blobs detection
    │
    ├── core/github_manager.py
    │       ├── PyGithub (github)← Repository CRUD via GitHub REST API
    │       └── requests         ← direct HTTP for template downloads
    │
    ├── ui/banner.py
    │       └── rich             ← Console, Panel, Text
    │
    └── ui/interactive.py
            ├── questionary      ← select, text, confirm prompts
            └── rich             ← Table, Panel rendering
```

---

*This document describes the architecture of `run-git` v1.4.0.*
