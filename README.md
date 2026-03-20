# RUN-GIT - Git Made Easy 🚀

```
╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃                                                                    ┃
┃    ██████╗ ██╗   ██╗███╗   ██╗      ██████╗ ██╗████████╗         ┃
┃    ██╔══██╗██║   ██║████╗  ██║     ██╔════╝ ██║╚══██╔══╝         ┃
┃    ██████╔╝██║   ██║██╔██╗ ██║     ██║  ███╗██║   ██║            ┃
┃    ██╔══██╗██║   ██║██║╚██╗██║     ██║   ██║██║   ██║            ┃
┃    ██║  ██║╚██████╔╝██║ ╚████║     ╚██████╔╝██║   ██║            ┃
┃    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝      ╚═════╝ ╚═╝   ╚═╝            ┃
┃                                                                    ┃
┃   ═══════════════════════════════════════════════════════════     ┃
┃                                                                    ┃
┃   ⚡ Git Operations Made Effortless                               ┃
┃   🎯 One Command | Zero Hassle | Full Control                     ┃
┃                                                                    ┃
┃   ┌──────────────────────────────────────────────────────────┐   ┃
┃   │  Developer    : Himanshu Kumar                           │   ┃
┃   │  GitHub       : @himanshu231204                          │   ┃
┃   │  Repository   : github.com/himanshu231204/gitpush        │   ┃
┃   │  Version      : v1.0.9                                   │   ┃
┃   │  License      : MIT                                      │   ┃
┃   └──────────────────────────────────────────────────────────┘   ┃
┃                                                                    ┃
┃   Type 'run-git help' to get started                              ┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
```

[![PyPI version](https://badge.fury.io/py/run-git.svg)](https://badge.fury.io/py/run-git)
[![Downloads](https://static.pepy.tech/badge/run-git)](https://pepy.tech/project/run-git)
[![Tests](https://github.com/himanshu231204/gitpush/workflows/Tests/badge.svg)](https://github.com/himanshu231204/gitpush/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**One Command To Rule Them All**

RUN-GIT is the ultimate Git automation tool designed to make Git operations effortless for developers of all skill levels. Say goodbye to complex Git commands and hello to simplicity!

Created by **Himanshu Kumar** ([@himanshu231204](https://github.com/himanshu231204))

---

## 🎯 Features

- ⚡ **Quick Push**: One command to add, commit, pull, and push
- 🤖 **Auto Commit Messages**: Intelligent commit message generation
- 🔀 **Interactive Conflict Resolution**: Easy-to-use conflict handling
- 🌿 **Branch Management**: Create, switch, delete, and merge branches effortlessly
- 📊 **Beautiful Status Display**: Rich terminal UI with colors and tables
- 🔐 **Sensitive File Detection**: Warns about .env, secrets, and credentials
- 🎨 **Interactive Mode**: Full TUI menu for all operations
- 🆕 **GitHub Repo Creation**: Create repositories from CLI or interactive menu
- 📂 **Smart Folder Detection**: Automatically detects existing files and asks for confirmation
- 🔄 **Existing Repo Support**: Connect existing local repos to GitHub
- 🔧 **Intelligent Remote Management**: Handles existing remotes gracefully
- 🚀 **Enhanced Push Reliability**: Fixed URL issues, token auth, auto-retry

---

🎯 Positioning
Tool	   Purpose
gh CLI	Power & flexibility
RUN-GIT	Speed & simplicity

---
💡 Use Cases

🚀 Hackathons

📚 Students / beginners

⚡ Quick projects

🔁 Daily commits

🧪 Prototyping

---
⚔️ Why Not Just Scripts?

Yes, you can write aliases or scripts.

But RUN-GIT provides:

✅ Zero setup

✅ Cross-platform support

✅ Error handling

✅ Interactive interface

✅ Smart automation

---

RUN-GIT is a “no-thinking layer” on top of Git, not a replacement for advanced tools.

## 📦 Installation

```bash
pip install run-git
```

---

## 🚀 Quick Start

### 1. Initialize Repository
```bash
# New repository
run-git init

# Clone existing repository
run-git init https://github.com/user/repo.git
```

### 2. Quick Push (Most Common Use Case)
```bash
# Add, commit, pull, and push in one command!
run-git push

# With custom commit message
run-git push -m "Add new feature"
```

### 3. Interactive Mode
```bash
# Just type run-git for interactive menu
run-git
```


### 💡 Creating Repositories

#### **Method 1: Interactive Menu** (Recommended)

```bash
run-git
```

Select **"🆕 Create New Repo"**

**Features:**
- 📂 Shows existing files
- 🔄 Handles existing repos
- 🔗 Manages remotes
- ✅ Confirms every step

#### **Method 2: CLI Quick Mode**
```bash
run-git new my-project --quick
```

#### **Method 3: CLI Interactive**
```bash
run-git new my-project
```

#### **Method 4: Full Command**
```bash
run-git new my-api -d "REST API" --public -g Python -l MIT
```

---

## 📖 Usage

### Basic Commands

```bash
# Push changes
run-git push

# View status
run-git status

# View commit history
run-git log

# Branch operations
run-git branch              # List branches
run-git branch feature-x    # Create branch
run-git switch main         # Switch branch
run-git merge feature-x     # Merge branch

# Remote management
run-git remote              # Show remotes

# Advanced
run-git pull                # Pull changes
run-git sync                # Pull + Push
run-git stash               # Stash changes
run-git undo                # Undo last commit
```

---

## 🤖 Auto Commit Messages

RUN-GIT generates intelligent commit messages:

- `feat: add authentication module (3 added)`
- `fix: update user validation (2 modified)`
- `docs: update README (1 modified)`
- `refactor: remove deprecated code (2 deleted)`

---

## 📚 Command Reference

| Command | Description |
|---------|-------------|
| `run-git` | Interactive mode with Create Repo |
| `run-git push` | Quick push (add, commit, pull, push) |
| `run-git new <n>` | Create new GitHub repository |
| `run-git init` | Initialize repository |
| `run-git status` | Show repository status |
| `run-git log` | Show commit history |
| `run-git branch` | List branches |
| `run-git switch <n>` | Switch branch |
| `run-git merge <n>` | Merge branch |
| `run-git remote` | Show remotes |
| `run-git pull` | Pull changes |
| `run-git sync` | Pull and push |
| `run-git stash` | Stash changes |
| `run-git undo` | Undo last commit |
| `run-git --help` | Show help |
| `run-git --version` | Show version |

---


---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Himanshu Kumar**
- GitHub: [@himanshu231204](https://github.com/himanshu231204)
- Created with ❤️ for the developer community

---

## 🌟 Show Your Support

If you find RUN-GIT helpful, please:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest new features
- 🔀 Contribute code

---




---

**Made with ❤️ by Himanshu Kumar | Making Git Easy for Everyone**
