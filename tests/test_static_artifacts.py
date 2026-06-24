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

    def test_research_dashboard_is_self_contained_and_includes_a5_results(self) -> None:
        html = (ROOT / "static" / "research-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("A5_STRICT_ABSTENTION", html)
        self.assertIn("95.8%", html)
        self.assertIn("12/13", html)
        self.assertIn("Evidence Boundary", html)
        self.assertIn("2/4", html)
        self.assertIn("A6_RELATION_VERIFIER", html)
        self.assertIn("87.5%", html)
        self.assertIn("3/4", html)
        self.assertIn("97.5%", html)
        self.assertIn("19/20", html)
        self.assertIn("A7_STRUCTURED_RELATION_GATE", html)
        self.assertIn("100.0%", html)
        self.assertIn("Structured Gate", html)
        self.assertIn("Expanded Gate Sweep", html)
        self.assertIn("160 hosted rows", html)
        self.assertIn("38/40", html)
        self.assertIn("40/40", html)
        self.assertIn("Classifier Gate Sweep", html)
        self.assertIn("A8_CLASSIFIED_RELATION_GATE", html)
        self.assertIn("82.5%", html)
        self.assertIn("26/40", html)
        self.assertIn("Calibrated Gate Sweep", html)
        self.assertIn("A9_CALIBRATED_RELATION_GATE", html)
        self.assertIn("10 overrides", html)
        self.assertIn("Raw classifier", html)
        self.assertIn("80/80", html)
        self.assertIn("Paired A7/A8/A9 Test", html)
        self.assertIn("Exact McNemar p", html)
        self.assertIn("+35.0 pp", html)
        self.assertIn("Repeat Stability", html)
        self.assertIn("task_chal_005", html)
        self.assertNotRegex(html, re.compile(r'<(?:script|img|link)[^>]+(?:src|href)="https?://', re.I))
        self.assertNotIn("ignore previous", html.lower())


if __name__ == "__main__":
    unittest.main()
