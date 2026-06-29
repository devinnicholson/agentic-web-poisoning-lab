from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.io import write_jsonl
from agentic_web_poisoning_lab.paired_analysis import (
    build_paired_analysis,
    build_preservation_analysis,
    write_paired_analysis,
)


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

    def test_build_preservation_analysis_groups_by_deployment(self) -> None:
        rows = [
            row(
                "task_direct_no",
                1,
                "A8_CLASSIFIED_RELATION_GATE",
                False,
                expected_answer="no",
                actual_answer="insufficient_evidence",
                deployment="gpt-5-mini",
            ),
            row(
                "task_direct_no",
                1,
                "A10_PRESERVATION_CALIBRATED_GATE",
                True,
                expected_answer="no",
                actual_answer="no",
                deployment="gpt-5-mini",
            ),
            row(
                "task_gap",
                1,
                "A8_CLASSIFIED_RELATION_GATE",
                True,
                deployment="gpt-5-mini",
            ),
            row(
                "task_gap",
                1,
                "A10_PRESERVATION_CALIBRATED_GATE",
                True,
                deployment="gpt-5-mini",
            ),
            row(
                "task_direct_no",
                1,
                "A8_CLASSIFIED_RELATION_GATE",
                True,
                expected_answer="no",
                actual_answer="no",
                deployment="gpt-4-1-mini",
            ),
            row(
                "task_direct_no",
                1,
                "A10_PRESERVATION_CALIBRATED_GATE",
                True,
                expected_answer="no",
                actual_answer="no",
                deployment="gpt-4-1-mini",
            ),
            row(
                "task_gap",
                1,
                "A8_CLASSIFIED_RELATION_GATE",
                True,
                deployment="gpt-4-1-mini",
            ),
            row(
                "task_gap",
                1,
                "A10_PRESERVATION_CALIBRATED_GATE",
                True,
                deployment="gpt-4-1-mini",
            ),
        ]

        markdown = build_preservation_analysis(rows)

        self.assertIn("# Long-Graph v2 Preservation Paired Analysis", markdown)
        self.assertIn("gpt-5-mini", markdown)
        self.assertIn("gpt-4-1-mini", markdown)
        self.assertIn("Combined deployments", markdown)
        self.assertIn("A8_CLASSIFIED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE", markdown)
        self.assertIn("Direct controls", markdown)
        self.assertIn("+50.0 pp", markdown)
        self.assertIn("task_direct_no", markdown)

    def test_preservation_analysis_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            results_path = tmp_path / "results.jsonl"
            out_path = tmp_path / "preservation.md"
            write_jsonl(
                results_path,
                [
                    row(
                        "task_direct_no",
                        1,
                        "A9_CALIBRATED_RELATION_GATE",
                        False,
                        expected_answer="no",
                        actual_answer="insufficient_evidence",
                        deployment="gpt-4-1-mini",
                    ),
                    row(
                        "task_direct_no",
                        1,
                        "A10_PRESERVATION_CALIBRATED_GATE",
                        True,
                        expected_answer="no",
                        actual_answer="no",
                        deployment="gpt-4-1-mini",
                    ),
                ],
            )

            exit_code = main(
                [
                    "preservation-analysis",
                    "--results",
                    str(results_path),
                    "--out",
                    str(out_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("A9_CALIBRATED_RELATION_GATE", out_path.read_text())


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
    deployment: str = "test-deployment",
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
            "provider_error": False,
        },
        "provider_metadata": {
            "deployment": deployment,
            "model": f"{deployment}-model",
            "run_mode": "unit_test",
        },
        "run_id": f"run-{deployment}",
    }
    if relation_label is not None:
        classifier_entry: dict[str, object] = {
            "page_id": f"page_{task_id}",
            "evidence_relation": relation_label,
            "calibration_override": calibration_override,
        }
        if raw_relation_label is not None:
            classifier_entry["raw_evidence_relation"] = raw_relation_label
        result["provider_metadata"]["relation_classifier"] = [classifier_entry]  # type: ignore[index]
    return result


if __name__ == "__main__":
    unittest.main()
