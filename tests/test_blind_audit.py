from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.blind_audit import (
    ResultRecord,
    build_blind_audit_artifacts,
)
from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.io import load_pages, read_jsonl, write_jsonl


class BlindAuditTest(unittest.TestCase):
    def test_build_blind_audit_hides_condition_and_raw_page_ids(self) -> None:
        row = first_public_row()
        pages = load_pages(ROOT / "data" / "pages.graph-long-v2.jsonl")

        queue, key = build_blind_audit_artifacts([ResultRecord(row)], pages, max_items=1)

        self.assertEqual(len(queue), 1)
        self.assertEqual(len(key), 1)
        packet = queue[0]
        packet_text = json.dumps(packet, sort_keys=True)
        self.assertIn("blind_", packet["audit_item_id"])
        self.assertIn("P01", packet_text)
        self.assertIn("review_labels", packet)
        self.assertEqual(packet["review_labels"]["answer_support"], None)

        self.assertNotIn(str(row["task_id"]), packet_text)
        self.assertNotIn(str(row["condition"]), packet_text)
        self.assertNotIn(str(row["expected_answer"]), packet_text)
        for page_id in row["visited_page_ids"]:
            self.assertNotIn(str(page_id), packet_text)
        self.assertNotIn("answer_accuracy", packet_text)
        self.assertNotIn("trust_label", packet_text)
        self.assertNotIn("is_poisoned", packet_text)
        self.assertNotIn("relation classifier gate", packet_text.lower())
        self.assertNotIn("direct_support", packet_text)
        self.assertNotIn("direct_refutation", packet_text)
        self.assertNotIn("missing_validation", packet_text)

        self.assertEqual(key[0]["audit_item_id"], packet["audit_item_id"])
        self.assertEqual(key[0]["task_id"], row["task_id"])
        self.assertEqual(key[0]["condition"], row["condition"])
        self.assertEqual(key[0]["expected_answer"], row["expected_answer"])
        self.assertIn("answer_accuracy", key[0]["metrics"])

    def test_blind_audit_cli_writes_queue_and_key(self) -> None:
        row = first_public_row()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            results_path = tmp_path / "results.jsonl"
            queue_path = tmp_path / "blind-queue.jsonl"
            key_path = tmp_path / "blind-key.jsonl"
            write_jsonl(results_path, [row])

            exit_code = main(
                [
                    "blind-audit",
                    "--results",
                    str(results_path),
                    "--pages",
                    str(ROOT / "data" / "pages.graph-long-v2.jsonl"),
                    "--out",
                    str(queue_path),
                    "--out-key",
                    str(key_path),
                    "--max-items",
                    "1",
                ]
            )

            self.assertEqual(exit_code, 0)
            queue_rows = read_jsonl(queue_path)
            key_rows = read_jsonl(key_path)
            self.assertEqual(len(queue_rows), 1)
            self.assertEqual(len(key_rows), 1)
            self.assertEqual(queue_rows[0]["audit_item_id"], key_rows[0]["audit_item_id"])

    def test_blind_audit_neutralizes_condition_style_conclusion_terms(self) -> None:
        row = first_public_row()
        row["answer"]["conclusion"] = (
            "Relation classifier gate: classifier-predicted trusted evidence relation is "
            "direct_support, but calibrated-relation gate rules mention missing_validation "
            "for page_v2_alert_validation_review and preservation-calibrated sources."
        )
        row["visited_page_ids"] = ["page_v2_alert_validation_review"]
        row["selected_page_ids"] = ["page_v2_alert_validation_review"]
        row["cited_page_ids"] = ["page_v2_alert_validation_review"]
        pages = load_pages(ROOT / "data" / "pages.graph-long-v2.jsonl")

        queue, _ = build_blind_audit_artifacts([ResultRecord(row)], pages, max_items=1)

        conclusion = queue[0]["response"]["conclusion"]
        self.assertIn("Evidence review note", conclusion)
        self.assertIn("P01", conclusion)
        self.assertNotIn("Relation classifier gate", conclusion)
        self.assertNotIn("classifier-predicted", conclusion)
        self.assertNotIn("direct_support", conclusion)
        self.assertNotIn("missing_validation", conclusion)
        self.assertNotIn("calibrated-relation gate", conclusion)
        self.assertNotIn("preservation-calibrated", conclusion)


def first_public_row() -> dict[str, object]:
    return read_jsonl(ROOT / "artifacts" / "long-graph-v2" / "hosted-gpt5-mini-results.jsonl")[0]


if __name__ == "__main__":
    unittest.main()
