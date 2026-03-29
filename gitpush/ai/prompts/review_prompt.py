"""Prompt template for AI PR review."""


def build_review_prompt(diff: str) -> str:
    """Build PR review prompt grounded in diff analysis."""

    return f"""Act as a senior engineer reviewing a pull request.

Analyze the code and find:
- Bugs
- Code quality issues
- Performance issues
- Best practice improvements

Rules:
- Be precise
- Do not hallucinate
- Only comment on real issues visible in diff
- Give actionable suggestions

Preferred output categories:
⚠️ Bug:
Description

Fix:
Suggested fix

💡 Code Smell:
Description

Suggestion:
Improvement

🚀 Performance:
Issue

Optimization:
Suggested fix

📌 Best Practice:
Suggestion

Code:
{diff}
"""
