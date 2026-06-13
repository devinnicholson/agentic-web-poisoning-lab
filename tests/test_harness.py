from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.agent import DeterministicWebAgent
from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.conditions import DEFAULT_CONDITIONS
from agentic_web_poisoning_lab.io import load_pages, load_tasks, read_jsonl
from agentic_web_poisoning_lab.metrics import summarize
from agentic_web_poisoning_lab.reporting import build_markdown_report


class HarnessTest(unittest.TestCase):
    def test_local_harness_separates_baseline_partial_and_full_defense(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.seed.jsonl")
        pages = load_pages(ROOT / "data" / "pages.seed.jsonl")
        rows = [row.to_dict() for row in DeterministicWebAgent(pages).run(tasks, DEFAULT_CONDITIONS)]
        summary = {row["condition"]: row for row in summarize(rows)}

        self.assertEqual(summary["A1_AGENT_BASELINE"]["attack_success_rate"], 1.0)
        self.assertGreater(summary["A3_PROMPT_SHIELDS"]["attack_success_rate"], 0.0)
        self.assertLess(
            summary["A3_PROMPT_SHIELDS"]["attack_success_rate"],
            summary["A1_AGENT_BASELINE"]["attack_success_rate"],
        )
        self.assertEqual(summary["A4_FULL_DEFENSE"]["attack_success_rate"], 0.0)
        self.assertEqual(summary["A4_FULL_DEFENSE"]["cited_poisoned_rate"], 0.0)
        self.assertGreater(summary["A4_FULL_DEFENSE"]["filtered_poisoned_rate"], 0.0)

    def test_action_hijack_is_unsafe_in_baseline_and_safe_in_prompt_shields(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.seed.jsonl")
        pages = load_pages(ROOT / "data" / "pages.seed.jsonl")
        rows = [row.to_dict() for row in DeterministicWebAgent(pages).run(tasks, DEFAULT_CONDITIONS)]

        baseline = find_row(rows, "task_003", "A1_AGENT_BASELINE")
        prompt_shields = find_row(rows, "task_003", "A3_PROMPT_SHIELDS")

        self.assertTrue(baseline["metrics"]["unsafe_action"])
        self.assertTrue(baseline["metrics"]["attack_success"])
        self.assertFalse(prompt_shields["metrics"]["unsafe_action"])
        self.assertFalse(prompt_shields["metrics"]["attack_success"])
        self.assertIn("page_supplement_action_hijack", prompt_shields["filtered_page_ids"])

    def test_report_includes_scorecard_and_notable_examples(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.seed.jsonl")
        pages = load_pages(ROOT / "data" / "pages.seed.jsonl")
        rows = [row.to_dict() for row in DeterministicWebAgent(pages).run(tasks, DEFAULT_CONDITIONS)]

        markdown = build_markdown_report(rows)

        self.assertIn("# Agentic Web Poisoning Report", markdown)
        self.assertIn("## Condition Scorecard", markdown)
        self.assertIn("Baseline attack success", markdown)
        self.assertIn("A4_FULL_DEFENSE", markdown)

    def test_cli_run_and_report_write_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "results"
            report_path = out_dir / "report.md"

            run_exit = main(["run", "--out-dir", str(out_dir)])
            report_exit = main(
                [
                    "report",
                    "--results",
                    str(out_dir / "results.jsonl"),
                    "--out",
                    str(report_path),
                ]
            )

            self.assertEqual(run_exit, 0)
            self.assertEqual(report_exit, 0)
            self.assertEqual(len(read_jsonl(out_dir / "results.jsonl")), 25)
            self.assertTrue((out_dir / "summary.json").exists())
            self.assertIn("Agentic Web Poisoning Report", report_path.read_text(encoding="utf-8"))


def find_row(rows: list[dict[str, object]], task_id: str, condition: str) -> dict[str, object]:
    for row in rows:
        if row["task_id"] == task_id and row["condition"] == condition:
            return row
    raise AssertionError(f"Missing row for {task_id} / {condition}")


if __name__ == "__main__":
    unittest.main()
