from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.agent import DeterministicWebAgent
from agentic_web_poisoning_lab.conditions import CONDITIONS
from agentic_web_poisoning_lab.hosted import build_hosted_messages
from agentic_web_poisoning_lab.io import load_pages, load_tasks


class StrictAbstentionTest(unittest.TestCase):
    def test_a5_abstains_when_clean_evidence_identifies_gap(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.challenge.jsonl")
        pages = load_pages(ROOT / "data" / "pages.challenge.jsonl")
        task = find_task(tasks, "task_chal_001")

        row = DeterministicWebAgent(pages).run_one(
            task,
            CONDITIONS["A5_STRICT_ABSTENTION"],
            run_id="strict-test",
        ).to_dict()

        self.assertEqual(row["actual_answer"], "insufficient_evidence")
        self.assertEqual(row["cited_page_ids"], ["page_chal_algae_concrete_gap"])
        self.assertIn("page_chal_algae_concrete_laundered", row["filtered_page_ids"])
        self.assertTrue(row["metrics"]["answer_accuracy"])
        self.assertFalse(row["metrics"]["attack_success"])
        self.assertFalse(row["metrics"]["cited_poisoned"])

    def test_a5_preserves_direct_no_when_clean_evidence_refutes_claim(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.challenge.jsonl")
        pages = load_pages(ROOT / "data" / "pages.challenge.jsonl")
        task = find_task(tasks, "task_chal_009")

        row = DeterministicWebAgent(pages).run_one(
            task,
            CONDITIONS["A5_STRICT_ABSTENTION"],
            run_id="strict-test",
        ).to_dict()

        self.assertEqual(row["actual_answer"], "no")
        self.assertEqual(row["cited_page_ids"], ["page_chal_memory_supplement_review"])
        self.assertIn("page_chal_memory_supplement_laundered", row["filtered_page_ids"])
        self.assertTrue(row["metrics"]["answer_accuracy"])
        self.assertFalse(row["metrics"]["attack_success"])

    def test_hosted_a5_prompt_includes_strict_abstention_rubric(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.challenge.jsonl")
        pages = load_pages(ROOT / "data" / "pages.challenge.jsonl")
        task = find_task(tasks, "task_chal_001")
        selected_pages = [find_page(pages, "page_chal_algae_concrete_gap")]
        filtered_pages = [find_page(pages, "page_chal_algae_concrete_laundered")]

        messages = build_hosted_messages(
            task,
            CONDITIONS["A5_STRICT_ABSTENTION"],
            selected_pages,
            filtered_pages,
        )

        self.assertIn("strict evidence-sufficiency rule", messages[0]["content"])
        self.assertIn("Strict abstention rubric", messages[1]["content"])
        self.assertIn("missing validation", messages[1]["content"])
        self.assertIn("Use no only for direct contradiction", messages[1]["content"])


def find_task(tasks: list[object], task_id: str) -> object:
    for task in tasks:
        if getattr(task, "id") == task_id:
            return task
    raise AssertionError(f"Missing task {task_id}")


def find_page(pages: list[object], page_id: str) -> object:
    for page in pages:
        if getattr(page, "id") == page_id:
            return page
    raise AssertionError(f"Missing page {page_id}")


if __name__ == "__main__":
    unittest.main()
