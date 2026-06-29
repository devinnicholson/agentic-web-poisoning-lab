from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.corpus_card import build_corpus_card
from agentic_web_poisoning_lab.io import write_jsonl
from agentic_web_poisoning_lab.schema import TaskCase, WebPage


class CorpusCardTest(unittest.TestCase):
    def test_build_corpus_card_summarizes_task_and_page_structure(self) -> None:
        tasks = [
            task("task_alert_gap", "insufficient_evidence", "source_laundering", "yes"),
            task("task_alert_no", "no", "source_laundering", "yes"),
            task("task_library_yes", "yes", "stale_page_conflict", "no", domain="library"),
        ]
        pages = [
            page("page_v2_alert_required_1", "trusted", "current", False, None, "task_alert_gap", "insufficient_evidence"),
            page("page_v2_alert_attack_1", "low", "current", True, "source_laundering", "task_alert_gap", "yes"),
            page("page_v2_library_required_1", "trusted", "current", False, None, "task_library_yes", "yes"),
        ]

        markdown = build_corpus_card(tasks, pages)

        self.assertIn("# Long-Graph v2 Corpus Card", markdown)
        self.assertIn("| Tasks | 3 |", markdown)
        self.assertIn("Expected answers", markdown)
        self.assertIn("insufficient_evidence=1; no=1; yes=1", markdown)
        self.assertIn("Poisoned pages", markdown)
        self.assertIn("False=2; True=1", markdown)
        self.assertIn("| alert | 2 | 2 |", markdown)
        self.assertIn("| library | 1 | 1 |", markdown)

    def test_corpus_card_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tasks_path = tmp_path / "tasks.jsonl"
            pages_path = tmp_path / "pages.jsonl"
            out_path = tmp_path / "corpus-card.md"
            write_jsonl(
                tasks_path,
                [
                    task_row(
                        "task_alert_yes",
                        "yes",
                        "source_laundering",
                        "no",
                        ["page_v2_alert_required_1"],
                        ["page_v2_alert_attack_1"],
                    )
                ],
            )
            write_jsonl(
                pages_path,
                [
                    page_row(
                        "page_v2_alert_required_1",
                        "trusted",
                        "current",
                        False,
                        None,
                        "task_alert_yes",
                        "yes",
                    ),
                    page_row(
                        "page_v2_alert_attack_1",
                        "low",
                        "current",
                        True,
                        "source_laundering",
                        "task_alert_yes",
                        "no",
                    ),
                ],
            )

            exit_code = main(
                [
                    "corpus-card",
                    "--tasks",
                    str(tasks_path),
                    "--pages",
                    str(pages_path),
                    "--out",
                    str(out_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("task_alert_yes", out_path.read_text(encoding="utf-8"))


def task(
    task_id: str,
    expected_answer: str,
    attack_type: str,
    attack_target_answer: str,
    domain: str = "alert",
) -> TaskCase:
    return TaskCase(
        id=task_id,
        question=f"Question for {task_id}?",
        expected_answer=expected_answer,
        required_page_ids=[f"page_v2_{domain}_required_1"],
        attack_page_ids=[f"page_v2_{domain}_attack_1"],
        attack_type=attack_type,
        attack_target_answer=attack_target_answer,
    )


def page(
    page_id: str,
    trust_label: str,
    freshness: str,
    is_poisoned: bool,
    attack_type: str | None,
    task_id: str,
    support: str,
) -> WebPage:
    return WebPage(
        id=page_id,
        title=f"Title for {page_id}",
        url=f"https://synthetic.local/{page_id}",
        source_type="policy",
        trust_label=trust_label,
        freshness=freshness,
        is_poisoned=is_poisoned,
        attack_type=attack_type,
        summary=f"Summary for {page_id}.",
        supports_tasks={task_id: support},
    )


def task_row(
    task_id: str,
    expected_answer: str,
    attack_type: str,
    attack_target_answer: str,
    required_page_ids: list[str],
    attack_page_ids: list[str],
) -> dict[str, object]:
    return {
        "id": task_id,
        "question": f"Question for {task_id}?",
        "expected_answer": expected_answer,
        "required_page_ids": required_page_ids,
        "attack_page_ids": attack_page_ids,
        "attack_type": attack_type,
        "attack_target_answer": attack_target_answer,
    }


def page_row(
    page_id: str,
    trust_label: str,
    freshness: str,
    is_poisoned: bool,
    attack_type: str | None,
    task_id: str,
    support: str,
) -> dict[str, object]:
    return {
        "id": page_id,
        "title": f"Title for {page_id}",
        "url": f"https://synthetic.local/{page_id}",
        "source_type": "policy",
        "trust_label": trust_label,
        "freshness": freshness,
        "is_poisoned": is_poisoned,
        "attack_type": attack_type,
        "summary": f"Summary for {page_id}.",
        "supports_tasks": {task_id: support},
    }
