from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.artifact_manifest import (
    ManifestEntry,
    build_artifact_manifest,
)
from agentic_web_poisoning_lab.cli import main


class ArtifactManifestTest(unittest.TestCase):
    def test_build_manifest_counts_records_and_hashes_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            rows_path = tmp_path / "rows.jsonl"
            doc_path = tmp_path / "doc.md"
            rows_path.write_text('{"a": 1}\n{"a": 2}\n', encoding="utf-8")
            doc_path.write_text("# Doc\n\nBody\n", encoding="utf-8")
            markdown = build_artifact_manifest(
                [
                    ManifestEntry("Rows", rows_path, "jsonl"),
                    ManifestEntry("Doc", doc_path, "markdown"),
                    ManifestEntry("Missing", tmp_path / "missing.jsonl", "jsonl"),
                ]
            )

            self.assertIn("# Research Artifact Manifest", markdown)
            self.assertIn("2 records", markdown)
            self.assertIn("3 lines", markdown)
            self.assertIn(hashlib.sha256(rows_path.read_bytes()).hexdigest(), markdown)
            self.assertIn(hashlib.sha256(doc_path.read_bytes()).hexdigest(), markdown)
            self.assertIn("| Missing |", markdown)
            self.assertIn("| missing | 0 | `missing` |", markdown)

    def test_artifact_manifest_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "manifest.md"

            exit_code = main(["artifact-manifest", "--out", str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            markdown = out_path.read_text(encoding="utf-8")
            self.assertIn("Research dashboard", markdown)
            self.assertIn("docs/long-graph-v2-preservation-transition-analysis.md", markdown)


if __name__ == "__main__":
    unittest.main()
