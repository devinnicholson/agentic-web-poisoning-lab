from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GraphDataTest(unittest.TestCase):
    def test_graph_tasks_reference_existing_pages(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.graph.jsonl")
        pages = read_jsonl(ROOT / "data" / "pages.graph.jsonl")
        page_ids = {page["id"] for page in pages}

        self.assertEqual(len(tasks), 12)
        self.assertEqual(len(pages), 36)
        for task in tasks:
            self.assertEqual(len(task["required_page_ids"]), 2)
            self.assertEqual(len(task["attack_page_ids"]), 2)
            for page_id in task["required_page_ids"] + task["attack_page_ids"]:
                self.assertIn(page_id, page_ids)

    def test_graph_set_has_balanced_answer_distribution_and_domains(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.graph.jsonl")
        expected_counts = {
            "yes": 0,
            "no": 0,
            "insufficient_evidence": 0,
        }
        for task in tasks:
            expected_counts[str(task["expected_answer"])] += 1

        self.assertEqual(expected_counts["yes"], 4)
        self.assertEqual(expected_counts["no"], 4)
        self.assertEqual(expected_counts["insufficient_evidence"], 4)
        self.assertEqual(
            {task["attack_type"] for task in tasks},
            {"source_laundering", "stale_page_conflict"},
        )

    def test_graph_required_pages_are_trusted_current_and_clean(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.graph.jsonl")
        pages = read_jsonl(ROOT / "data" / "pages.graph.jsonl")
        by_id = {page["id"]: page for page in pages}

        for task in tasks:
            for page_id in task["required_page_ids"]:
                page = by_id[page_id]
                self.assertEqual(page["trust_label"], "trusted")
                self.assertEqual(page["freshness"], "current")
                self.assertFalse(page["is_poisoned"])
                self.assertEqual(page["supports_tasks"][task["id"]], task["expected_answer"])

    def test_graph_attack_pages_are_poisoned_and_redacted(self) -> None:
        pages = read_jsonl(ROOT / "data" / "pages.graph.jsonl")
        attack_pages = [page for page in pages if page["is_poisoned"]]

        self.assertEqual(len(attack_pages), 12)
        self.assertEqual(
            {page["attack_type"] for page in attack_pages},
            {"source_laundering", "stale_page_conflict", "confidence_pressure"},
        )
        self.assertEqual(sum(1 for page in attack_pages if page["freshness"] == "stale"), 4)
        self.assertEqual(sum(1 for page in attack_pages if page["trust_label"] == "low"), 8)
        for page in attack_pages:
            self.assertIsNotNone(page["attack_type"])
            self.assertNotIn("ignore previous", page["summary"].lower())
            self.assertNotIn("system prompt", page["summary"].lower())

    def test_long_graph_tasks_reference_existing_pages(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.graph-long.jsonl")
        pages = read_jsonl(ROOT / "data" / "pages.graph-long.jsonl")
        page_ids = {page["id"] for page in pages}

        self.assertEqual(len(tasks), 12)
        self.assertEqual(len(pages), 48)
        for task in tasks:
            self.assertEqual(len(task["required_page_ids"]), 3)
            self.assertEqual(len(task["attack_page_ids"]), 3)
            for page_id in task["required_page_ids"] + task["attack_page_ids"]:
                self.assertIn(page_id, page_ids)

    def test_long_graph_set_has_balanced_answer_distribution(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.graph-long.jsonl")
        expected_counts = {
            "yes": 0,
            "no": 0,
            "insufficient_evidence": 0,
        }
        for task in tasks:
            expected_counts[str(task["expected_answer"])] += 1

        self.assertEqual(expected_counts["yes"], 4)
        self.assertEqual(expected_counts["no"], 4)
        self.assertEqual(expected_counts["insufficient_evidence"], 4)
        self.assertEqual(
            {task["attack_type"] for task in tasks},
            {"source_laundering", "stale_page_conflict"},
        )

    def test_long_graph_required_pages_are_trusted_current_and_clean(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.graph-long.jsonl")
        pages = read_jsonl(ROOT / "data" / "pages.graph-long.jsonl")
        by_id = {page["id"]: page for page in pages}

        for task in tasks:
            for page_id in task["required_page_ids"]:
                page = by_id[page_id]
                self.assertEqual(page["trust_label"], "trusted")
                self.assertEqual(page["freshness"], "current")
                self.assertFalse(page["is_poisoned"])
                self.assertEqual(page["supports_tasks"][task["id"]], task["expected_answer"])

    def test_long_graph_attack_pages_are_poisoned_and_redacted(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.graph-long.jsonl")
        pages = read_jsonl(ROOT / "data" / "pages.graph-long.jsonl")
        attack_pages = [page for page in pages if page["is_poisoned"]]
        by_id = {page["id"]: page for page in pages}

        self.assertEqual(len(attack_pages), 12)
        self.assertEqual(
            {page["attack_type"] for page in attack_pages},
            {"source_laundering", "stale_page_conflict", "confidence_pressure"},
        )
        self.assertEqual(sum(1 for page in attack_pages if page["freshness"] == "stale"), 4)
        self.assertEqual(sum(1 for page in attack_pages if page["trust_label"] == "low"), 8)
        for task in tasks:
            for page_id in task["attack_page_ids"]:
                self.assertIn(task["id"], by_id[page_id]["supports_tasks"])
        for page in attack_pages:
            self.assertIsNotNone(page["attack_type"])
            self.assertNotIn("ignore previous", page["summary"].lower())
            self.assertNotIn("system prompt", page["summary"].lower())


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


if __name__ == "__main__":
    unittest.main()
