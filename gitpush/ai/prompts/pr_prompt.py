"""Prompt template for PR description generation."""

from typing import List


def build_pr_prompt(diff: str, commit_messages: List[str]) -> str:
    """Build PR description prompt with strict output structure."""

    commits_section = (
        "\n".join(f"- {message}" for message in commit_messages) or "- No recent commits"
    )

    return f"""You are a senior developer.

Generate a professional pull request description.

STRICT FORMAT:
## Summary
<High-level explanation>

## Changes
- change 1
- change 2
- change 3

## Impact
- performance impact
- breaking changes
- user impact

## Testing
- how it was tested

Rules:
- No vague text
- Keep output readable and specific
- Stay grounded in provided inputs only

Recent commit messages:
{commits_section}

Diff:
{diff}
"""
