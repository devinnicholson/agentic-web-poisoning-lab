from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.io import write_jsonl
from agentic_web_poisoning_lab.research_stats import build_research_stats, write_research_stats


class ResearchStatsTest(unittest.TestCase):
    def test_build_research_stats_includes_intervals_and_defense_delta(self) -> None:
        rows = [
            row("task_001", "A1_AGENT_BASELINE", answer_accuracy=False, attack_success=True, cited_poisoned=True),
            row("task_001", "A4_FULL_DEFENSE", answer_accuracy=True, attack_success=False, cited_poisoned=False),
        ]

        markdown = build_research_stats(rows)

        self.assertIn("# Research Statistics", markdown)
        self.assertIn("95% CI", markdown)
        self.assertIn("A4_FULL_DEFENSE", markdown)
        self.assertIn("+100.0 pp (100.0% -> 0.0%)", markdown)
        self.assertIn("+100.0 pp (0.0% -> 100.0%)", markdown)

    def test_write_research_stats_and_cli_stats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            results_path = tmp_path / "results.jsonl"
            out_path = tmp_path / "nested" / "stats.md"
            write_jsonl(
                results_path,
                [
                    row("task_001", "A1_AGENT_BASELINE", answer_accuracy=False, attack_success=True),
                    row(
                        "task_002",
                        "A1_AGENT_BASELINE",
                        answer_accuracy=False,
                        expected_answer="insufficient_evidence",
                    ),
                ],
            )

            markdown = write_research_stats(results_path, out_path)
            exit_code = main(
                [
                    "stats",
                    "--results",
                    str(results_path),
                    "--out",
                    str(tmp_path / "cli-stats.md"),
                ]
            )

            self.assertTrue(out_path.exists())
            self.assertIn("Abstention Calibration", markdown)
            self.assertIn("Answer Confusion Matrix", markdown)
            self.assertIn("False Non-Abstain Examples", markdown)
            self.assertIn("task_002", markdown)
            self.assertEqual(exit_code, 0)
            self.assertTrue((tmp_path / "cli-stats.md").exists())

    def test_build_research_stats_includes_repeat_stability_when_repeat_index_exists(self) -> None:
        rows = [
            row(
                "task_bound_003",
                "A5_STRICT_ABSTENTION",
                answer_accuracy=False,
                expected_answer="insufficient_evidence",
                actual_answer="no",
                repeat_index=1,
            ),
            row(
                "task_bound_003",
                "A5_STRICT_ABSTENTION",
                answer_accuracy=True,
                expected_answer="insufficient_evidence",
                actual_answer="insufficient_evidence",
                repeat_index=2,
            ),
        ]

        markdown = build_research_stats(rows)

        self.assertIn("Repeat Stability", markdown)
        self.assertIn("task_bound_003", markdown)
        self.assertIn("1/2", markdown)
        self.assertIn("no=1; insufficient_evidence=1", markdown)


def row(
    task_id: str,
    condition: str,
    answer_accuracy: bool = True,
    attack_success: bool = False,
    cited_poisoned: bool = False,
    expected_answer: str = "no",
    actual_answer: str = "no",
    repeat_index: int | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "task_id": task_id,
        "condition": condition,
        "attack_type": "stale_page_conflict",
        "expected_answer": expected_answer,
        "actual_answer": actual_answer,
        "latency_ms": 250,
        "provider_metadata": {
            "model": "fake-hosted-model",
            "retry_count": 1,
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        },
        "metrics": {
            "answer_accuracy": answer_accuracy,
            "attack_success": attack_success,
            "cited_poisoned": cited_poisoned,
            "filtered_poisoned": not cited_poisoned,
            "unsafe_action": False,
            "provider_block": False,
            "provider_error": False,
        },
    }
    if repeat_index is not None:
        result["repeat_index"] = repeat_index
    return result


if __name__ == "__main__":
    unittest.main()
