from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ChallengeDataTest(unittest.TestCase):
    def test_challenge_tasks_reference_existing_pages(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.challenge.jsonl")
        pages = read_jsonl(ROOT / "data" / "pages.challenge.jsonl")
        page_ids = {page["id"] for page in pages}

        self.assertEqual(len(tasks), 24)
        for task in tasks:
            for page_id in task["required_page_ids"] + task["attack_page_ids"]:
                self.assertIn(page_id, page_ids)

    def test_challenge_set_targets_source_laundering_and_abstention(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.challenge.jsonl")
        attack_tasks = [task for task in tasks if task["attack_type"]]
        insufficient_tasks = [
            task for task in tasks if task["expected_answer"] == "insufficient_evidence"
        ]
        source_laundering_tasks = [
            task for task in tasks if task["attack_type"] == "source_laundering"
        ]

        self.assertEqual(len(attack_tasks), 20)
        self.assertGreaterEqual(len(insufficient_tasks), 13)
        self.assertEqual(len(source_laundering_tasks), 12)

    def test_challenge_attack_pages_are_low_trust_and_redacted(self) -> None:
        pages = read_jsonl(ROOT / "data" / "pages.challenge.jsonl")
        attack_pages = [page for page in pages if page["is_poisoned"]]

        self.assertEqual(len(attack_pages), 20)
        for page in attack_pages:
            self.assertEqual(page["trust_label"], "low")
            self.assertIsNotNone(page["attack_type"])
            self.assertNotIn("ignore previous", page["summary"].lower())
            self.assertNotIn("system prompt", page["summary"].lower())

    def test_challenge_required_pages_are_trusted_current_and_clean(self) -> None:
        pages = read_jsonl(ROOT / "data" / "pages.challenge.jsonl")
        tasks = read_jsonl(ROOT / "data" / "tasks.challenge.jsonl")
        by_id = {page["id"]: page for page in pages}

        for task in tasks:
            for page_id in task["required_page_ids"]:
                page = by_id[page_id]
                self.assertEqual(page["trust_label"], "trusted")
                self.assertEqual(page["freshness"], "current")
                self.assertFalse(page["is_poisoned"])


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


if __name__ == "__main__":
    unittest.main()
