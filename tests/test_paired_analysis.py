from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.io import write_jsonl
from agentic_web_poisoning_lab.paired_analysis import build_paired_analysis, write_paired_analysis


class PairedAnalysisTest(unittest.TestCase):
    def test_build_paired_analysis_reports_deltas_and_classifier_taxonomy(self) -> None:
        rows = [
            row("task_bound_003", 1, "A7_STRUCTURED_RELATION_GATE", True),
            row(
                "task_bound_003",
                1,
                "A8_CLASSIFIED_RELATION_GATE",
                False,
                actual_answer="no",
                relation_label="direct_refutation",
            ),
            row(
                "task_bound_003",
                1,
                "A9_CALIBRATED_RELATION_GATE",
                True,
                relation_label="missing_validation",
                raw_relation_label="direct_refutation",
                calibration_override=True,
            ),
            row(
                "task_bound_004",
                1,
                "A7_STRUCTURED_RELATION_GATE",
                True,
                expected_answer="no",
                actual_answer="no",
            ),
            row(
                "task_bound_004",
                1,
                "A8_CLASSIFIED_RELATION_GATE",
                True,
                expected_answer="no",
                actual_answer="no",
                relation_label="direct_refutation",
            ),
            row(
                "task_bound_004",
                1,
                "A9_CALIBRATED_RELATION_GATE",
                True,
                expected_answer="no",
                actual_answer="no",
                relation_label="direct_refutation",
            ),
        ]

        markdown = build_paired_analysis(rows)

        self.assertIn("# Paired Condition Analysis", markdown)
        self.assertIn("A8_CLASSIFIED_RELATION_GATE -> A9_CALIBRATED_RELATION_GATE", markdown)
        self.assertIn("+50.0 pp", markdown)
        self.assertIn("Relation Label Taxonomy", markdown)
        self.assertIn("direct_refutation=1", markdown)
        self.assertIn("missing_validation=1", markdown)
        self.assertIn("Calibration Overrides", markdown)
        self.assertIn("direct_refutation -> missing_validation=1", markdown)
        self.assertIn("Failure Inventory", markdown)
        self.assertIn("task_bound_003", markdown)

    def test_write_paired_analysis_and_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            results_path = tmp_path / "results.jsonl"
            out_path = tmp_path / "paired.md"
            cli_out_path = tmp_path / "cli-paired.md"
            write_jsonl(
                results_path,
                [
                    row("task_bound_003", 1, "A8_CLASSIFIED_RELATION_GATE", False),
                    row("task_bound_003", 1, "A9_CALIBRATED_RELATION_GATE", True),
                ],
            )

            markdown = write_paired_analysis([results_path], out_path)
            exit_code = main(
                [
                    "paired-analysis",
                    "--results",
                    str(results_path),
                    "--out",
                    str(cli_out_path),
                ]
            )

            self.assertTrue(out_path.exists())
            self.assertIn("Paired Accuracy Deltas", markdown)
            self.assertEqual(exit_code, 0)
            self.assertTrue(cli_out_path.exists())


def row(
    task_id: str,
    repeat_index: int,
    condition: str,
    answer_accuracy: bool,
    expected_answer: str = "insufficient_evidence",
    actual_answer: str = "insufficient_evidence",
    relation_label: str | None = None,
    raw_relation_label: str | None = None,
    calibration_override: bool = False,
) -> dict[str, object]:
    result: dict[str, object] = {
        "task_id": task_id,
        "repeat_index": repeat_index,
        "condition": condition,
        "expected_answer": expected_answer,
        "actual_answer": actual_answer,
        "attack_type": "source_laundering",
        "cited_page_ids": [f"page_{task_id}"],
        "metrics": {
            "answer_accuracy": answer_accuracy,
            "attack_success": False,
            "cited_poisoned": False,
        },
    }
    if relation_label is not None:
        classifier_entry: dict[str, object] = {
            "page_id": f"page_{task_id}",
            "evidence_relation": relation_label,
            "calibration_override": calibration_override,
        }
        if raw_relation_label is not None:
            classifier_entry["raw_evidence_relation"] = raw_relation_label
        result["provider_metadata"] = {"relation_classifier": [classifier_entry]}
    return result


if __name__ == "__main__":
    unittest.main()
