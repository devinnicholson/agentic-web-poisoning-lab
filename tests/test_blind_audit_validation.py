from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.blind_audit import audit_item_id_for_row
from agentic_web_poisoning_lab.blind_audit_validation import (
    DEFAULT_BLIND_AUDIT_VALIDATION_SPEC,
    build_blind_audit_validation,
)
from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.io import read_jsonl


class BlindAuditValidationTest(unittest.TestCase):
    def test_committed_blind_audit_packet_validates(self) -> None:
        spec = DEFAULT_BLIND_AUDIT_VALIDATION_SPEC
        markdown = build_blind_audit_validation(
            read_jsonl(ROOT / spec.queue_path),
            read_jsonl(ROOT / spec.key_path),
            source_rows(spec.results_paths),
            spec,
        )

        self.assertIn("# Long-Graph v2 Blind Audit Validation", markdown)
        self.assertIn("- PASS: no validation issues found.", markdown)
        self.assertNotIn("| FAIL |", markdown)
        self.assertIn("| Blind queue rows | 576 |", markdown)
        self.assertIn("| Forbidden leakage scan | PASS |", markdown)

    def test_validation_fails_when_queue_exposes_condition(self) -> None:
        spec = DEFAULT_BLIND_AUDIT_VALIDATION_SPEC
        one_source_row = source_rows(spec.results_paths)[:1]
        audit_id = audit_item_id_for_row(one_source_row[0][2])
        queue = [
            dict(row)
            for row in read_jsonl(ROOT / spec.queue_path)
            if row["audit_item_id"] == audit_id
        ]
        key = [
            dict(row)
            for row in read_jsonl(ROOT / spec.key_path)
            if row["audit_item_id"] == audit_id
        ]
        queue[0]["condition"] = "A10_PRESERVATION_CALIBRATED_GATE"

        markdown = build_blind_audit_validation(queue, key, one_source_row, spec)

        self.assertIn("| Queue does not expose key-only fields | FAIL | condition |", markdown)
        self.assertIn("| Forbidden leakage scan | FAIL |", markdown)
        self.assertIn("A10_PRESERVATION_CALIBRATED_GATE", markdown)

    def test_blind_audit_validation_cli_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "blind-audit-validation.md"

            exit_code = main(["blind-audit-validation", "--out", str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            markdown = out_path.read_text(encoding="utf-8")
            self.assertIn("- PASS: no validation issues found.", markdown)


def source_rows(results_paths: tuple[Path, ...]) -> list[tuple[Path, int, dict[str, object]]]:
    rows: list[tuple[Path, int, dict[str, object]]] = []
    for path in results_paths:
        for line, row in enumerate(read_jsonl(ROOT / path), start=1):
            rows.append((path, line, row))
    return rows


if __name__ == "__main__":
    unittest.main()
