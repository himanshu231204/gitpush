# Task Context: SPEC AI Features

Session ID: 2026-03-30-spec-ai-features
Created: 2026-03-30T00:00:00Z
Status: in_progress

## Current Request
Implement all features defined in SPEC.md: `commit-ai`, `pr-ai`, and `review-ai`, following the architecture and folder structure in SPEC without adding out-of-scope features.

## Context Files (Standards to Follow)
- `.opencode/context/core/standards/code-quality.md`
- `.opencode/context/core/standards/test-coverage.md`
- `.opencode/context/core/workflows/feature-breakdown.md`

## Reference Files (Source Material to Look At)
- `SPEC.md`
- `gitpush/cli.py`
- `gitpush/commands/__init__.py`
- `gitpush/core/git_operations.py`
- `gitpush/ui/banner.py`
- `gitpush/exceptions.py`

## External Docs Fetched
None (implementation scoped to project spec and existing dependencies).

## Components
- AI provider system (factory + base provider + concrete providers)
- AI prompts (commit/pr/review)
- AI client abstraction
- AI core engine orchestration
- CLI commands (`commit-ai`, `pr-ai`, `review-ai`)
- Diff cleaning utility

## Constraints
- Keep architecture separation: commands → core → ai
- Keep behavior grounded in git diff input
- Handle edge cases from SPEC (empty diff, binary lines, large diffs)

## Exit Criteria
- [ ] `run-git commit-ai` implemented and wired
- [ ] `run-git pr-ai` implemented and wired
- [ ] `run-git review-ai` implemented and wired
- [ ] AI layer supports OpenAI, Anthropic, and Local via factory + base interface
- [ ] Tests added for new core behavior
