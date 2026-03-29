"""Utilities for preparing git diff text for AI models."""

from __future__ import annotations

from typing import Dict, List


class DiffCleaner:
    """Clean and summarize diffs for stable AI processing."""

    _BINARY_MARKERS = ("Binary files ", "GIT binary patch")
    _REMOVED_METADATA_PREFIXES = (
        "index ",
        "new file mode ",
        "deleted file mode ",
        "old mode ",
        "new mode ",
    )

    def clean_git_diff(self, raw_diff: str) -> str:
        """Remove unnecessary metadata and binary sections from diff."""

        if not raw_diff or not raw_diff.strip():
            return ""

        cleaned_lines: List[str] = []
        for line in raw_diff.splitlines():
            if self._is_binary_line(line):
                continue
            if line.startswith(self._REMOVED_METADATA_PREFIXES):
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def prepare_for_ai(self, raw_diff: str, max_chars: int, chunk_size: int) -> str:
        """Return cleaned diff or summarized representation for huge diffs."""

        cleaned = self.clean_git_diff(raw_diff)
        if not cleaned:
            return ""

        if len(cleaned) <= max_chars:
            return cleaned

        return self.summarize_large_diff(cleaned, max_chars=max_chars, chunk_size=chunk_size)

    def summarize_large_diff(self, cleaned_diff: str, max_chars: int, chunk_size: int) -> str:
        """Summarize a large diff using chunk-aware extraction."""

        chunks = self.chunk_diff(cleaned_diff, chunk_size=chunk_size)
        files = self._collect_file_stats(cleaned_diff)

        lines = [
            "Large diff detected. Chunked summary provided.",
            f"Total chunks: {len(chunks)}",
            "",
            "Files changed:",
        ]

        for file_path, stats in files.items():
            lines.append(
                f"- {file_path}: +{stats['additions']} -{stats['deletions']} ({stats['hunks']} hunks)"
            )

        lines.extend(["", "Representative diff excerpt:"])
        lines.append(chunks[0][: max(500, min(len(chunks[0]), 6000))])

        summary = "\n".join(lines).strip()
        if len(summary) > max_chars:
            summary = summary[: max_chars - 40].rstrip() + "\n\n...[truncated summary]"
        return summary

    def chunk_diff(self, cleaned_diff: str, chunk_size: int = 8000) -> List[str]:
        """Chunk cleaned diff by size while preserving line boundaries."""

        if not cleaned_diff:
            return []

        chunks: List[str] = []
        current_lines: List[str] = []
        current_size = 0

        for line in cleaned_diff.splitlines():
            line_size = len(line) + 1
            if current_lines and current_size + line_size > chunk_size:
                chunks.append("\n".join(current_lines))
                current_lines = []
                current_size = 0

            current_lines.append(line)
            current_size += line_size

        if current_lines:
            chunks.append("\n".join(current_lines))

        return chunks

    @staticmethod
    def is_empty(diff_text: str) -> bool:
        """Return True when no meaningful diff content exists."""

        return not diff_text or not diff_text.strip()

    def _is_binary_line(self, line: str) -> bool:
        return any(line.startswith(marker) for marker in self._BINARY_MARKERS)

    def _collect_file_stats(self, diff_text: str) -> Dict[str, Dict[str, int]]:
        """Collect file-level stats from diff text."""

        stats: Dict[str, Dict[str, int]] = {}
        current_file = "unknown"

        for line in diff_text.splitlines():
            if line.startswith("diff --git "):
                current_file = _extract_path_from_diff_header(line)
                stats.setdefault(current_file, {"additions": 0, "deletions": 0, "hunks": 0})
                continue

            if line.startswith("@@"):
                stats.setdefault(current_file, {"additions": 0, "deletions": 0, "hunks": 0})
                stats[current_file]["hunks"] += 1
                continue

            if line.startswith("+") and not line.startswith("+++"):
                stats.setdefault(current_file, {"additions": 0, "deletions": 0, "hunks": 0})
                stats[current_file]["additions"] += 1
                continue

            if line.startswith("-") and not line.startswith("---"):
                stats.setdefault(current_file, {"additions": 0, "deletions": 0, "hunks": 0})
                stats[current_file]["deletions"] += 1

        return stats


def _extract_path_from_diff_header(header_line: str) -> str:
    """Extract file path from `diff --git a/x b/x` header."""

    parts = header_line.split()
    if len(parts) < 4:
        return "unknown"
    b_path = parts[3]
    if b_path.startswith("b/"):
        return b_path[2:]
    return b_path
