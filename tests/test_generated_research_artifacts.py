from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.artifact_manifest import build_artifact_manifest
from agentic_web_poisoning_lab.corpus_card import build_corpus_card
from agentic_web_poisoning_lab.io import load_pages, load_tasks, read_jsonl
from agentic_web_poisoning_lab.paired_analysis import build_preservation_analysis
from agentic_web_poisoning_lab.preservation_casebook import build_preservation_casebook
from agentic_web_poisoning_lab.preservation_transitions import (
    build_preservation_transition_analysis,
)
from agentic_web_poisoning_lab.public_snapshot import snapshot_is_public_safe


LONG_GRAPH_V2_RESULTS = [
    Path("artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl"),
    Path("artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl"),
]
LONG_GRAPH_V2_TASKS = Path("data/tasks.graph-long-v2.jsonl")
LONG_GRAPH_V2_PAGES = Path("data/pages.graph-long-v2.jsonl")


class GeneratedResearchArtifactsTest(unittest.TestCase):
    def test_committed_long_graph_v2_corpus_card_is_current(self) -> None:
        expected = build_corpus_card(
            load_tasks(ROOT / LONG_GRAPH_V2_TASKS),
            load_pages(ROOT / LONG_GRAPH_V2_PAGES),
            LONG_GRAPH_V2_TASKS,
            LONG_GRAPH_V2_PAGES,
        )
        actual = (ROOT / "docs/long-graph-v2-corpus-card.md").read_text(encoding="utf-8")

        self.assertEqual(actual, expected)

    def test_committed_public_snapshots_are_redacted(self) -> None:
        self.assertTrue(snapshot_is_public_safe(_long_graph_v2_rows()))

    def test_committed_paired_preservation_appendix_is_current(self) -> None:
        rows = _long_graph_v2_rows()
        expected = build_preservation_analysis(rows, source_paths=LONG_GRAPH_V2_RESULTS)
        actual = (ROOT / "docs/paired-long-graph-v2-preservation-analysis.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(actual, expected)

    def test_committed_preservation_casebook_is_current(self) -> None:
        rows = _long_graph_v2_rows()
        expected = build_preservation_casebook(
            rows,
            load_pages(ROOT / LONG_GRAPH_V2_PAGES),
            source_paths=LONG_GRAPH_V2_RESULTS,
            pages_path=LONG_GRAPH_V2_PAGES,
        )
        actual = (ROOT / "docs/long-graph-v2-preservation-casebook.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(actual, expected)

    def test_committed_transition_appendix_is_current(self) -> None:
        rows = _long_graph_v2_rows()
        expected = build_preservation_transition_analysis(
            rows,
            load_pages(ROOT / LONG_GRAPH_V2_PAGES),
            source_paths=LONG_GRAPH_V2_RESULTS,
            pages_path=LONG_GRAPH_V2_PAGES,
        )
        actual = (
            ROOT / "docs/long-graph-v2-preservation-transition-analysis.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(actual, expected)

    def test_committed_artifact_manifest_is_current(self) -> None:
        expected = build_artifact_manifest()
        actual = (ROOT / "docs/research-artifact-manifest.md").read_text(encoding="utf-8")

        self.assertEqual(actual, expected)


def _long_graph_v2_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in LONG_GRAPH_V2_RESULTS:
        rows.extend(read_jsonl(ROOT / path))
    return rows


if __name__ == "__main__":
    unittest.main()
