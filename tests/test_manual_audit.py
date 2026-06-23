from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SOURCE_SELECTION = {
    "clean_only",
    "mixed_clean_and_poisoned",
    "poisoned_only",
    "none",
}
CITATION_QUALITY = {
    "supported",
    "partial",
    "unsupported",
    "poisoned",
    "stale",
    "none",
}
ATTACK_HANDLING = {
    "followed",
    "contaminated",
    "ignored",
    "filtered",
    "not_applicable",
}
ABSTENTION_QUALITY = {
    "correct_abstain",
    "false_non_abstain",
    "false_abstain",
    "not_applicable",
}


class ManualAuditTest(unittest.TestCase):
    def test_hosted_challenge_manual_audit_references_challenge_tasks(self) -> None:
        tasks = read_jsonl(ROOT / "data" / "tasks.challenge.jsonl")
        rows = read_jsonl(ROOT / "data" / "manual-audit.hosted-challenge.jsonl")
        task_ids = {task["id"] for task in tasks}

        self.assertGreaterEqual(len(rows), 6)
        for row in rows:
            self.assertEqual(row["run_id"], "hosted-20260623T153515Z")
            self.assertIn(row["task_id"], task_ids)
            self.assertIn(row["condition"], {
                "A1_AGENT_BASELINE",
                "A2_SOURCE_RANKING",
                "A3_PROMPT_SHIELDS",
                "A4_FULL_DEFENSE",
            })

    def test_hosted_challenge_manual_audit_uses_known_labels(self) -> None:
        rows = read_jsonl(ROOT / "data" / "manual-audit.hosted-challenge.jsonl")

        for row in rows:
            self.assertIn(row["source_selection"], SOURCE_SELECTION)
            self.assertIn(row["citation_quality"], CITATION_QUALITY)
            self.assertIn(row["attack_handling"], ATTACK_HANDLING)
            self.assertIn(row["abstention_quality"], ABSTENTION_QUALITY)
            self.assertIn(row["adjudicated_answer"], {"yes", "no", "insufficient_evidence"})
            self.assertRegex(row["review_priority"], r"^P[0-2]$")
            self.assertTrue(str(row["notes"]).strip())


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


if __name__ == "__main__":
    unittest.main()
