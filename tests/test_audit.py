from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.agent import DeterministicWebAgent
from agentic_web_poisoning_lab.audit import build_audit_queue, write_audit_queue
from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.conditions import DEFAULT_CONDITIONS
from agentic_web_poisoning_lab.io import load_pages, load_tasks, write_jsonl


class AuditTest(unittest.TestCase):
    def test_build_audit_queue_prioritizes_unsafe_actions_and_attack_successes(self) -> None:
        rows, pages = local_rows_and_pages()

        markdown = build_audit_queue(rows, pages, max_rows=12)

        self.assertIn("# Agentic Web Human Audit Queue", markdown)
        self.assertIn("## Priority Rules", markdown)
        self.assertIn("unsafe action", markdown)
        self.assertIn("attack success", markdown)
        self.assertIn("Manual labels:", markdown)
        self.assertIn("page_supplement_action_hijack", markdown)

    def test_write_audit_queue_reads_and_writes_markdown(self) -> None:
        rows, _ = local_rows_and_pages()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            results_path = tmp_path / "results.jsonl"
            out_path = tmp_path / "nested" / "audit.md"
            write_jsonl(results_path, rows)

            markdown = write_audit_queue(
                results_path,
                ROOT / "data" / "pages.seed.jsonl",
                out_path,
                max_rows=8,
            )

            self.assertTrue(out_path.exists())
            self.assertEqual(out_path.read_text(encoding="utf-8"), markdown)
            self.assertIn("Queue Coverage", markdown)

    def test_cli_audit_command_writes_queue(self) -> None:
        rows, _ = local_rows_and_pages()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            results_path = tmp_path / "results.jsonl"
            out_path = tmp_path / "audit.md"
            write_jsonl(results_path, rows)

            exit_code = main(
                [
                    "audit",
                    "--results",
                    str(results_path),
                    "--pages",
                    str(ROOT / "data" / "pages.seed.jsonl"),
                    "--out",
                    str(out_path),
                    "--max-rows",
                    "5",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("Agentic Web Human Audit Queue", out_path.read_text(encoding="utf-8"))


def local_rows_and_pages() -> tuple[list[dict[str, object]], object]:
    tasks = load_tasks(ROOT / "data" / "tasks.seed.jsonl")
    pages = load_pages(ROOT / "data" / "pages.seed.jsonl")
    rows = [row.to_dict() for row in DeterministicWebAgent(pages).run(tasks, DEFAULT_CONDITIONS)]
    return rows, pages


if __name__ == "__main__":
    unittest.main()
