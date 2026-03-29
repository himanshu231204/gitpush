"""Prompt template for commit message generation."""


def build_commit_prompt(diff: str) -> str:
    """Build commit prompt with strict conventional commit rules."""

    return f"""You are an expert software engineer.

Generate a conventional commit message from this git diff.

Rules:
- Follow conventional commit format
- Supported types only: feat, fix, refactor, docs, chore, test
- Keep summary under 72 characters
- Add bullet points for key changes
- Stay grounded in the provided diff

Output format:
<type>(scope): short summary

- change 1
- change 2
- change 3

Diff:
{diff}
"""
