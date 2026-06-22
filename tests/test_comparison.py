from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.comparison import build_comparison_report, write_comparison_report
from agentic_web_poisoning_lab.io import write_jsonl


class ComparisonTest(unittest.TestCase):
    def test_build_comparison_report_pairs_local_and_hosted_rows(self) -> None:
        local_rows = [
            row(
                actual_answer="yes",
                answer_accuracy=False,
                attack_success=True,
                cited_poisoned=True,
            )
        ]
        hosted_rows = [
            row(
                actual_answer="no",
                answer_accuracy=True,
                attack_success=False,
                cited_poisoned=False,
                provider_metadata={"model": "fake-hosted-model", "finish_reason": "stop"},
            )
        ]

        markdown = build_comparison_report(local_rows, hosted_rows)

        self.assertIn("# Hosted vs Local Comparison", markdown)
        self.assertIn("Local attack successes recovered by hosted model | 1", markdown)
        self.assertIn("fake-hosted-model", markdown)
        self.assertIn("Risk Deltas", markdown)

    def test_write_comparison_report_and_cli_compare(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            local_path = tmp_path / "local.jsonl"
            hosted_path = tmp_path / "hosted.jsonl"
            out_path = tmp_path / "nested" / "comparison.md"
            write_jsonl(local_path, [row(actual_answer="yes", answer_accuracy=False)])
            write_jsonl(hosted_path, [row(actual_answer="no", answer_accuracy=True)])

            markdown = write_comparison_report(local_path, hosted_path, out_path)
            exit_code = main(
                [
                    "compare",
                    "--local",
                    str(local_path),
                    "--hosted",
                    str(hosted_path),
                    "--out",
                    str(tmp_path / "cli-comparison.md"),
                ]
            )

            self.assertTrue(out_path.exists())
            self.assertIn("Answer Deltas", markdown)
            self.assertEqual(exit_code, 0)
            self.assertTrue((tmp_path / "cli-comparison.md").exists())


def row(
    actual_answer: str,
    answer_accuracy: bool,
    attack_success: bool = False,
    cited_poisoned: bool = False,
    provider_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "task_id": "task_011",
        "condition": "A1_AGENT_BASELINE",
        "attack_type": "action_hijack",
        "expected_answer": "no",
        "actual_answer": actual_answer,
        "latency_ms": 250,
        "provider_metadata": provider_metadata or {},
        "metrics": {
            "answer_accuracy": answer_accuracy,
            "attack_success": attack_success,
            "cited_poisoned": cited_poisoned,
            "filtered_poisoned": False,
            "provider_block": False,
            "provider_error": False,
        },
    }


if __name__ == "__main__":
    unittest.main()
