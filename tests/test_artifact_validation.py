from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.artifact_validation import (
    PublicSnapshotValidationSpec,
    build_public_artifact_validation,
)
from agentic_web_poisoning_lab.metrics import summarize
from agentic_web_poisoning_lab.public_snapshot import REDACTED_VALUE
from agentic_web_poisoning_lab.schema import TaskCase, WebPage


class ArtifactValidationTest(unittest.TestCase):
    def test_build_public_artifact_validation_passes_consistent_snapshot(self) -> None:
        tasks = [
            TaskCase(
                id="task_001",
                question="Question?",
                expected_answer="yes",
                required_page_ids=["page_001"],
                attack_page_ids=[],
                attack_type=None,
                attack_target_answer=None,
            )
        ]
        pages = [
            WebPage(
                id="page_001",
                title="Page",
                url="https://example.test/page",
                source_type="policy",
                trust_label="trusted",
                freshness="current",
                is_poisoned=False,
                attack_type=None,
                summary="Summary",
                supports_tasks={"task_001": "direct_support"},
            )
        ]
        rows = [
            {
                "condition": "A10_PRESERVATION_CALIBRATED_GATE",
                "task_id": "task_001",
                "expected_answer": "yes",
                "actual_answer": "yes",
                "cited_page_ids": ["page_001"],
                "filtered_page_ids": [],
                "selected_page_ids": ["page_001"],
                "visited_page_ids": ["page_001"],
                "latency_ms": 10,
                "estimated_cost_usd": 0.0,
                "metrics": {
                    "answer_accuracy": True,
                    "attack_success": False,
                    "cited_poisoned": False,
                    "filtered_poisoned": False,
                    "provider_block": False,
                    "provider_error": False,
                    "unsafe_action": False,
                },
                "provider_metadata": {
                    "endpoint_host": REDACTED_VALUE,
                    "response_id": REDACTED_VALUE,
                    "system_fingerprint": REDACTED_VALUE,
                },
            }
        ]
        spec = PublicSnapshotValidationSpec(
            "Test snapshot",
            Path("artifacts/test/results.jsonl"),
            Path("artifacts/test/summary.json"),
            {"A10_PRESERVATION_CALIBRATED_GATE": 1},
        )

        markdown = build_public_artifact_validation(
            tasks,
            pages,
            Path("data/tasks.test.jsonl"),
            Path("data/pages.test.jsonl"),
            [(spec, rows, summarize(rows))],
        )

        self.assertIn("# Long-Graph v2 Public Artifact Validation", markdown)
        self.assertIn("| Test snapshot | 1 | PASS | PASS | PASS | 0 | 0 |", markdown)
        self.assertIn("- PASS: no validation issues found.", markdown)


if __name__ == "__main__":
    unittest.main()
