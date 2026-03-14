# Changelog

## [1.0.6] - 2026-03-15
 
### 🆕 Added
- **Interactive Menu Integration**: "Create New Repo" option now available in interactive mode
  - Access via `run-git` → Select "🆕 Create New Repo"
  - Full interactive workflow with guided prompts
  - Same powerful features as CLI command
 
### 🔧 Improved
- **Enhanced Push Reliability**: Improved repository push mechanism with automatic retry
  - Smart branch management (ensures `main` branch)
  - Automatic sync with remote on conflicts
  - Graceful error handling with manual fallback options
- **Better Git Add**: Using `git.add(A=True)` for more reliable file staging
- **Branch Naming**: Automatically uses `main` branch (not `master`)
- **Conflict Resolution**: Auto-handles unrelated histories with `--allow-unrelated-histories`
 
### 🐛 Fixed
- Fixed push failures when remote has diverged
- Improved error messages for failed operations
- Better handling of repository state conflicts
- Fixed branch naming inconsistencies
 
### 📚 Documentation
- Updated README with interactive mode usage
- Enhanced troubleshooting section
- Added error handling examples

---
## 📦 RUN-GIT v1.0.5 – 2026-03-13

### ✨ Improvements

* Improved **Git push reliability** during repository creation.
* Ensured default branch is automatically set to **main**.
* Replaced `git add *` with `git add -A` for better file tracking.
* Improved repository initialization workflow.

### 🐛 Bug Fixes

* Fixed **"refusing to merge unrelated histories"** error during first push.
* Fixed push failures when GitHub repository already contained commits.
* Improved handling of repositories with existing remote configuration.

### 🔧 Internal Changes

* Added retry logic for push operations.
* Automatic **pull + sync** if initial push fails.
* Improved CLI stability and error messages.

### 🚀 Example

```bash
run-git new my-project --quick
```

Creates a GitHub repository and pushes it instantly.

### 📦 Installation

```bash
pip install --upgrade run-git
```

### 🔗 Repository

https://github.com/himanshu231204/gitpush

---

⭐ If you find this project useful, consider giving it a star.


## [1.0.4] - 2026-03-13
 
### 🆕 Added
- **GitHub Repository Creation**: New `run-git new` command to create GitHub repositories directly from terminal
  - Smart language detection (Python, Node, Java, Go, Rust, and 160+ more)
  - Auto-generates .gitignore files for detected languages
  - License support (MIT, Apache 2.0, GPL v3, BSD, ISC)
  - Professional README template generation
  - One-time GitHub token setup with secure storage
  - Quick mode (`--quick`) for instant repo creation with smart defaults
  - Interactive mode for full customization
- Secure token storage in `~/.run-git/config.yml` with user-only permissions
- Automatic repo name conflict detection with suggestions
- Support for public and private repositories
 
### 🔧 Improved
- Enhanced error handling for network issues
- Better user feedback with progress indicators
- Cross-platform token storage support (Windows/Mac/Linux)
- Improved documentation with detailed setup guides
 
### 🐛 Fixed
- Token validation improvements
- Better handling of existing repositories
- Enhanced cross-platform compatibility
## [1.0.0] - 2026

### Added
- 🎉 Initial release of gitpush
- ⚡ Quick push command
- 🤖 Intelligent commit messages
- 🔀 Interactive conflict resolution
- 🌿 Branch management
- 📊 Beautiful terminal UI
- 🔐 Sensitive file detection

Created by: Himanshu Kumar (@himanshu231204)
