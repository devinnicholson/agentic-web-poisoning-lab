from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StaticArtifactsTest(unittest.TestCase):
    def test_action_hijack_case_study_is_self_contained_and_redacted(self) -> None:
        html = (ROOT / "static" / "action-hijack-case-study.html").read_text(encoding="utf-8")

        self.assertIn("task_011", html)
        self.assertIn("page_housing_grant_hijack", html)
        self.assertIn("Raw instruction text is redacted", html)
        self.assertNotRegex(html, re.compile(r'<(?:script|img|link)[^>]+(?:src|href)="https?://', re.I))
        self.assertNotIn("ignore previous", html.lower())


if __name__ == "__main__":
    unittest.main()
