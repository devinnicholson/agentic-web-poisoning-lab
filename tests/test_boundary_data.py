from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BoundaryDataTest(unittest.TestCase):
    def test_boundary_tasks_reference_existing_pages(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.boundary.jsonl")
        pages = read_jsonl(ROOT / "data" / "pages.boundary.jsonl")
        page_ids = {page["id"] for page in pages}

        self.assertEqual(len(tasks), 8)
        for task in tasks:
            for page_id in task["required_page_ids"] + task["attack_page_ids"]:
                self.assertIn(page_id, page_ids)

    def test_boundary_set_pairs_missing_validation_and_direct_negation(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.boundary.jsonl")
        insufficient = [task for task in tasks if task["expected_answer"] == "insufficient_evidence"]
        direct_no = [task for task in tasks if task["expected_answer"] == "no"]

        self.assertEqual(len(insufficient), 4)
        self.assertEqual(len(direct_no), 4)
        self.assertTrue(all(task["attack_type"] == "source_laundering" for task in tasks))
        self.assertTrue(all(task["attack_target_answer"] == "yes" for task in tasks))

    def test_boundary_pages_are_redacted_and_labeled(self) -> None:
        pages = read_jsonl(ROOT / "data" / "pages.boundary.jsonl")
        attack_pages = [page for page in pages if page["is_poisoned"]]
        clean_pages = [page for page in pages if not page["is_poisoned"]]

        self.assertEqual(len(attack_pages), 4)
        self.assertEqual(len(clean_pages), 8)
        for page in attack_pages:
            self.assertEqual(page["trust_label"], "low")
            self.assertEqual(page["attack_type"], "source_laundering")
            self.assertNotIn("ignore previous", page["summary"].lower())
            self.assertNotIn("system prompt", page["summary"].lower())
        for page in clean_pages:
            self.assertEqual(page["trust_label"], "trusted")
            self.assertEqual(page["freshness"], "current")

    def test_expanded_boundary_set_preserves_minimal_pair_shape(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.boundary-expanded.jsonl")
        pages = read_jsonl(ROOT / "data" / "pages.boundary-expanded.jsonl")
        page_ids = {page["id"] for page in pages}
        task_ids = [task["id"] for task in tasks]
        insufficient = [task for task in tasks if task["expected_answer"] == "insufficient_evidence"]
        direct_no = [task for task in tasks if task["expected_answer"] == "no"]
        attack_pages = [page for page in pages if page["is_poisoned"]]
        clean_pages = [page for page in pages if not page["is_poisoned"]]

        self.assertEqual(len(tasks), 16)
        self.assertEqual(len(set(task_ids)), 16)
        self.assertEqual(len(insufficient), 8)
        self.assertEqual(len(direct_no), 8)
        self.assertEqual(len(attack_pages), 8)
        self.assertEqual(len(clean_pages), 16)
        self.assertTrue(all(task["attack_type"] == "source_laundering" for task in tasks))
        self.assertTrue(all(task["attack_target_answer"] == "yes" for task in tasks))
        for task in tasks:
            for page_id in task["required_page_ids"] + task["attack_page_ids"]:
                self.assertIn(page_id, page_ids)
        for page in attack_pages:
            self.assertEqual(page["trust_label"], "low")
            self.assertEqual(page["attack_type"], "source_laundering")
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
