"""Prompt template for AI PR review."""

import os


def _load_template(filename: str) -> str:
    """Load prompt template from the prompts directory."""
    prompts_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(prompts_dir, filename)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def build_review_prompt(diff: str) -> str:
    """Build comprehensive PR review prompt for thorough analysis."""
    template = _load_template("review_prompt_template.md")
    return template.format(diff=diff)
