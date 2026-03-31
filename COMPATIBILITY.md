# RUN-GIT Compatibility Guide

This document outlines the compatibility requirements and supported environments for RUN-GIT.

---

## Python Version Support

| Version | Status | Notes |
|---------|--------|-------|
| **Python 3.8** | ✅ Supported | Minimum required version |
| **Python 3.9** | ✅ Supported | Actively tested in CI |
| **Python 3.10** | ✅ Supported | Actively tested in CI |
| **Python 3.11** | ✅ Supported | Actively tested in CI |
| **Python 3.12** | ✅ Compatible | Should work (not actively tested) |
| **Python 2.x** | ❌ Not Supported | End of life |

**Requirement**: `requires-python = ">=3.8"`

---

## Operating System Support

| OS | Status | Notes |
|----|--------|-------|
| **Linux** | ✅ Full Support | All features work |
| **macOS** | ✅ Full Support | All features work |
| **Windows** | ✅ Full Support | PowerShell/CMD compatible |
| **BSD** | ✅ Compatible | Should work (untested) |

### Windows Specific

- PowerShell commands are used for compatibility
- Cross-platform path handling via `pathlib`
- Line endings handled automatically by GitPython

---

## Git Version Requirements

| Version | Status | Notes |
|---------|--------|-------|
| **Git 2.x** | ✅ Required | Minimum version needed |
| **Git 2.20+** | ✅ Recommended | Better performance |
| **Git 2.30+** | ✅ Recommended | Modern features |

**Requirement**: Git must be installed and available in PATH.

### Verify Git Installation

```bash
git --version
# Expected: git version 2.x.x or higher
```

---

## Dependency Compatibility

### Core Dependencies

| Package | Minimum Version | Purpose |
|---------|-----------------|---------|
| `click` | ≥ 8.0.0 | CLI framework |
| `rich` | ≥ 13.0.0 | Terminal UI |
| `GitPython` | ≥ 3.1.0 | Git operations |
| `PyGithub` | ≥ 1.59.0 | GitHub API |
| `questionary` | ≥ 1.10.0 | Interactive prompts |
| `pyyaml` | ≥ 6.0 | Config files |
| `requests` | ≥ 2.28.0 | HTTP requests |

### Optional Dependencies

| Package | Purpose | Notes |
|---------|---------|-------|
| `pytest` | Testing | For running tests |
| `pytest-cov` | Test coverage | Optional |
| `black` | Code formatting | For development |
| `flake8` | Linting | For development |
| `pylint` | Advanced linting | Optional |

---

## Required External Tools

### Git Executable

RUN-GIT requires Git to be installed on the system. It uses GitPython which wraps the `git` command-line tool.

**Verification**:
```bash
which git        # Linux/macOS
where git       # Windows
```

### GitHub Token (for GitHub features)

For GitHub repository creation and other GitHub API features:

- Requires GitHub Personal Access Token (PAT)
- Required scopes: `repo`, `user`
- Stored in `~/.run-git/config.yml`

---

## Shell Compatibility

| Shell | Status | Notes |
|-------|--------|-------|
| **bash** | ✅ Full Support | Linux/macOS default |
| **zsh** | ✅ Full Support | macOS default (modern) |
| **PowerShell** | ✅ Full Support | Windows default |
| **cmd** | ✅ Full Support | Windows legacy |
| **fish** | ✅ Compatible | Should work |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GIT_PREFIX` | No | Git executable path |
| `RUN_GIT_AI_PROVIDER` | No | AI provider (openai/anthropic/etc.) |
| `OPENAI_API_KEY` | No | For AI features (OpenAI) |
| `ANTHROPIC_API_KEY` | No | For AI features (Anthropic) |
| `GOOGLE_API_KEY` | No | For AI features (Google) |

---

## Known Limitations

### Platform-Specific

| Issue | Platform | Status |
|-------|----------|--------|
| TUI colors | Windows CMD | Reduced (no truecolor) |
| Shell prompts | Windows CMD | Limited compatibility |
| Path separators | Windows | Handled automatically |

### Feature-Specific

| Feature | Limitation |
|---------|------------|
| AI features | Requires API key for respective provider |
| GitHub integration | Requires GitHub token |
| Interactive TUI | Requires terminal with ANSI support |

---

## Installation Methods

### Recommended

```bash
pip install run-git
```

### Development Mode

```bash
git clone https://github.com/himanshu231204/run-git.git
cd run-git
pip install -e ".[dev]"
```

### From Source

```bash
python -m pip install .
```

---

## Testing Matrix

| Python | Linux | macOS | Windows |
|--------|-------|-------|---------|
| 3.8 | ✅ | ✅ | ✅ |
| 3.9 | ✅ | ✅ | ✅ |
| 3.10 | ✅ | ✅ | ✅ |
| 3.11 | ✅ | ✅ | ✅ |

---

## Troubleshooting

### "git: command not found"

**Solution**: Install Git and ensure it's in your PATH.

### "Python 3.7 or lower"

**Solution**: Upgrade to Python 3.8+.

### "ModuleNotFoundError"

**Solution**: Reinstall dependencies:
```bash
pip install --upgrade run-git
```

---

## Support

For compatibility issues or questions:
- **Issues**: https://github.com/himanshu231204/run-git/issues
- **Discussions**: https://github.com/himanshu231204/run-git/discussions

---

*Last updated: 2026-03-31*
