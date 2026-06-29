from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.cli import main
from agentic_web_poisoning_lab.io import read_jsonl, write_jsonl
from agentic_web_poisoning_lab.public_snapshot import (
    REDACTED_VALUE,
    sanitize_result_row,
    snapshot_is_public_safe,
)


class PublicSnapshotTest(unittest.TestCase):
    def test_sanitize_result_row_redacts_provider_identifiers(self) -> None:
        row = {
            "condition": "A10_PRESERVATION_CALIBRATED_GATE",
            "metrics": {"answer_accuracy": True},
            "provider_metadata": {
                "deployment": "gpt-5-mini",
                "endpoint_host": "private-resource.openai.azure.com",
                "response_id": "chatcmpl-secret",
                "system_fingerprint": "fp_secret",
            },
        }

        sanitized = sanitize_result_row(row)

        self.assertEqual(
            sanitized["provider_metadata"]["endpoint_host"],
            REDACTED_VALUE,
        )
        self.assertEqual(sanitized["provider_metadata"]["response_id"], REDACTED_VALUE)
        self.assertEqual(
            sanitized["provider_metadata"]["system_fingerprint"],
            REDACTED_VALUE,
        )
        self.assertEqual(sanitized["provider_metadata"]["deployment"], "gpt-5-mini")
        self.assertTrue(snapshot_is_public_safe([sanitized]))
        self.assertFalse(snapshot_is_public_safe([row]))

    def test_public_snapshot_cli_writes_sanitized_rows_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            results_path = tmp_path / "results.jsonl"
            out_results = tmp_path / "public" / "results.jsonl"
            out_summary = tmp_path / "public" / "summary.json"
            write_jsonl(
                results_path,
                [
                    {
                        "condition": "A10_PRESERVATION_CALIBRATED_GATE",
                        "expected_answer": "yes",
                        "actual_answer": "yes",
                        "metrics": {
                            "answer_accuracy": True,
                            "attack_success": False,
                            "cited_poisoned": False,
                            "filtered_poisoned": False,
                            "provider_block": False,
                            "provider_error": False,
                            "unsafe_action": False,
                        },
                        "provider_metadata": {
                            "endpoint_host": "private-resource.openai.azure.com",
                            "provider": "azure_openai",
                            "response_id": "chatcmpl-secret",
                        },
                    }
                ],
            )

            exit_code = main(
                [
                    "public-snapshot",
                    "--results",
                    str(results_path),
                    "--out-results",
                    str(out_results),
                    "--out-summary",
                    str(out_summary),
                ]
            )

            self.assertEqual(exit_code, 0)
            rows = read_jsonl(out_results)
            self.assertTrue(snapshot_is_public_safe(rows))
            self.assertIn('"A10_PRESERVATION_CALIBRATED_GATE"', out_summary.read_text())


if __name__ == "__main__":
    unittest.main()
