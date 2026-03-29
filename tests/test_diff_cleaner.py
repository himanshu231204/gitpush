"""Tests for git diff cleaning and summarization."""

import unittest

from gitpush.utils.diff_cleaner import DiffCleaner


class TestDiffCleaner(unittest.TestCase):
    """Diff cleaner unit tests."""

    def setUp(self):
        self.cleaner = DiffCleaner()

    def test_clean_git_diff_removes_metadata_and_binary(self):
        raw = """diff --git a/a.py b/a.py
index 123..456 100644
--- a/a.py
+++ b/a.py
@@ -1 +1 @@
-old
+new
Binary files a/image.png and b/image.png differ
"""
        cleaned = self.cleaner.clean_git_diff(raw)
        self.assertNotIn("index 123..456", cleaned)
        self.assertNotIn("Binary files", cleaned)
        self.assertIn("+new", cleaned)

    def test_chunk_diff_splits_large_diff(self):
        diff = "\n".join(f"+line {i}" for i in range(500))
        chunks = self.cleaner.chunk_diff(diff, chunk_size=200)
        self.assertGreater(len(chunks), 1)

    def test_prepare_for_ai_summarizes_huge_diff(self):
        raw = "\n".join(
            ["diff --git a/file.py b/file.py"]
            + [f"+added line {i}" for i in range(3000)]
        )
        prepared = self.cleaner.prepare_for_ai(raw, max_chars=1000, chunk_size=300)
        self.assertIn("Large diff detected", prepared)
        self.assertIn("Files changed", prepared)


if __name__ == "__main__":
    unittest.main()
