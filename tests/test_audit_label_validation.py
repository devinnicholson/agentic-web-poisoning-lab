from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.audit_label_validation import (
    AuditLabelValidationSpec,
    build_audit_label_validation,
)
from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.io import read_jsonl, write_jsonl


class AuditLabelValidationTest(unittest.TestCase):
    def test_valid_label_row_passes(self) -> None:
        queue = first_queue_rows()
        labels = [valid_label_for(queue[0])]

        markdown = build_audit_label_validation(labels, queue)

        self.assertIn("- PASS: no validation issues found.", markdown)
        self.assertIn("| Label rows | 1 |", markdown)
        self.assertNotIn("| FAIL |", markdown)

    def test_invalid_label_row_reports_schema_and_reference_errors(self) -> None:
        queue = first_queue_rows()
        bad = valid_label_for(queue[0])
        bad["review_round"] = "draft"
        bad["page_relation_labels"] = {"P99": "direct_support"}
        bad["leakage_flags"] = ["none", "condition_seen"]
        labels = [bad, dict(bad)]

        markdown = build_audit_label_validation(labels, queue)

        self.assertIn("| Rows parse as label records | FAIL |", markdown)
        self.assertIn("duplicate review keys", markdown)
        self.assertIn("review_round must be one of", markdown)
        self.assertIn("non-cited refs", markdown)
        self.assertIn("cannot combine none", markdown)

    def test_audit_label_validation_cli_writes_report(self) -> None:
        queue = first_queue_rows()
        labels = [valid_label_for(queue[0])]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            labels_path = tmp_path / "labels.jsonl"
            out_path = tmp_path / "label-validation.md"
            write_jsonl(labels_path, labels)

            exit_code = main(
                [
                    "audit-label-validation",
                    "--labels",
                    str(labels_path),
                    "--queue",
                    str(ROOT / "artifacts" / "long-graph-v2" / "blind-audit-queue.jsonl"),
                    "--out",
                    str(out_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("- PASS: no validation issues found.", out_path.read_text(encoding="utf-8"))


def first_queue_rows() -> list[dict[str, object]]:
    return read_jsonl(ROOT / "artifacts" / "long-graph-v2" / "blind-audit-queue.jsonl")[:3]


def valid_label_for(queue_row: dict[str, object]) -> dict[str, object]:
    response = queue_row["response"]
    assert isinstance(response, dict)
    citation_refs = [str(ref) for ref in response["citation_refs"]]
    return {
        "audit_item_id": queue_row["audit_item_id"],
        "reviewer_id": "reviewer_a",
        "review_round": "initial",
        "adjudicated_answer": "insufficient_evidence",
        "answer_label_confidence": "high",
        "source_selection": "clean_only",
        "citation_quality": "supported",
        "attack_handling": "ignored",
        "abstention_quality": "correct_abstain",
        "page_relation_labels": {ref: "missing_validation" for ref in citation_refs},
        "leakage_flags": ["none"],
        "notes": "Cited aliases support an evidence-gap label without exposing raw IDs.",
    }


if __name__ == "__main__":
    unittest.main()
