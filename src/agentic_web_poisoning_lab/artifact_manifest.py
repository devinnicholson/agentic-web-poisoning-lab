from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from agentic_web_poisoning_lab.io import write_text


@dataclass(frozen=True)
class ManifestEntry:
    label: str
    path: Path
    kind: str


DEFAULT_MANIFEST_ENTRIES = (
    ManifestEntry("Long-graph v2 tasks", Path("data/tasks.graph-long-v2.jsonl"), "jsonl"),
    ManifestEntry("Long-graph v2 pages", Path("data/pages.graph-long-v2.jsonl"), "jsonl"),
    ManifestEntry(
        "Primary hosted long-graph v2 rows",
        Path("experiments/results/hosted-long-graph-v2-pilot/results.jsonl"),
        "jsonl",
    ),
    ManifestEntry(
        "Cross-model hosted long-graph v2 rows",
        Path("experiments/results/hosted-long-graph-v2-gpt41mini-a8-a10-repeats/results.jsonl"),
        "jsonl",
    ),
    ManifestEntry(
        "Primary hosted long-graph v2 summary",
        Path("experiments/results/hosted-long-graph-v2-pilot/summary.json"),
        "json",
    ),
    ManifestEntry(
        "Cross-model hosted long-graph v2 summary",
        Path("experiments/results/hosted-long-graph-v2-gpt41mini-a8-a10-repeats/summary.json"),
        "json",
    ),
    ManifestEntry(
        "Paired preservation appendix",
        Path("docs/paired-long-graph-v2-preservation-analysis.md"),
        "markdown",
    ),
    ManifestEntry(
        "Preservation repair casebook",
        Path("docs/long-graph-v2-preservation-casebook.md"),
        "markdown",
    ),
    ManifestEntry(
        "Preservation transition appendix",
        Path("docs/long-graph-v2-preservation-transition-analysis.md"),
        "markdown",
    ),
    ManifestEntry(
        "Primary hosted long-graph v2 narrative",
        Path("docs/hosted-long-graph-v2-summary.md"),
        "markdown",
    ),
    ManifestEntry(
        "Cross-model hosted long-graph v2 narrative",
        Path("docs/hosted-long-graph-v2-cross-model-summary.md"),
        "markdown",
    ),
    ManifestEntry("Research dashboard", Path("static/research-dashboard.html"), "html"),
)


def write_artifact_manifest(
    out_path: Path,
    entries: Sequence[ManifestEntry] = DEFAULT_MANIFEST_ENTRIES,
) -> str:
    markdown = build_artifact_manifest(entries)
    write_text(out_path, markdown)
    return markdown


def build_artifact_manifest(
    entries: Sequence[ManifestEntry] = DEFAULT_MANIFEST_ENTRIES,
) -> str:
    artifact_rows = [_artifact_row(entry) for entry in entries]
    lines = [
        "# Research Artifact Manifest",
        "",
        (
            "This deterministic manifest records the key public artifacts for the "
            "long-graph v2 preservation finding. It avoids timestamps so it can be "
            "regenerated and diffed cleanly."
        ),
        "",
        "## Regeneration Commands",
        "",
        "```bash",
        "make paired-analysis-long-graph-v2-preservation",
        "make casebook-long-graph-v2-preservation",
        "make transition-analysis-long-graph-v2-preservation",
        "make artifact-manifest-refresh",
        "```",
        "",
        "## Artifact Checksums",
        "",
        "| Artifact | Path | Kind | Records/lines | Bytes | SHA-256 |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in artifact_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(row["label"]),
                    f"`{_cell(row['path'])}`",
                    _cell(row["kind"]),
                    _cell(row["count"]),
                    row["bytes"],
                    f"`{row['sha256']}`",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Claim Map",
            "",
            "| Claim | Primary artifacts |",
            "| --- | --- |",
            (
                "| A10 repairs direct-control over-abstention across two deployments | "
                "`docs/paired-long-graph-v2-preservation-analysis.md`, "
                "`docs/hosted-long-graph-v2-summary.md`, "
                "`docs/hosted-long-graph-v2-cross-model-summary.md` |"
            ),
            (
                "| Row-level repairs are inspectable against trusted/current pages | "
                "`docs/long-graph-v2-preservation-casebook.md`, "
                "`data/pages.graph-long-v2.jsonl` |"
            ),
            (
                "| Page-label changes are concentrated on repaired rows | "
                "`docs/long-graph-v2-preservation-transition-analysis.md`, "
                "`experiments/results/hosted-long-graph-v2-pilot/results.jsonl`, "
                "`experiments/results/hosted-long-graph-v2-gpt41mini-a8-a10-repeats/results.jsonl` |"
            ),
            (
                "| Public dashboard summarizes the committed aggregate results | "
                "`static/research-dashboard.html` |"
            ),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _artifact_row(entry: ManifestEntry) -> dict[str, str]:
    path = entry.path
    if not path.exists():
        return {
            "label": entry.label,
            "path": str(path),
            "kind": entry.kind,
            "count": "missing",
            "bytes": "0",
            "sha256": "missing",
        }

    data = path.read_bytes()
    return {
        "label": entry.label,
        "path": str(path),
        "kind": entry.kind,
        "count": _record_or_line_count(path, entry.kind),
        "bytes": str(len(data)),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _record_or_line_count(path: Path, kind: str) -> str:
    text = path.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    if kind == "jsonl":
        record_count = sum(1 for line in text.splitlines() if line.strip())
        return f"{record_count} records"
    return f"{line_count} lines"


def _cell(value: str) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")
