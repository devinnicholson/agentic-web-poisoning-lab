from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_web_poisoning_lab.io import load_pages, load_tasks, read_jsonl, write_text
from agentic_web_poisoning_lab.metrics import summarize
from agentic_web_poisoning_lab.public_snapshot import snapshot_is_public_safe
from agentic_web_poisoning_lab.schema import TaskCase, WebPage


@dataclass(frozen=True)
class PublicSnapshotValidationSpec:
    label: str
    results_path: Path
    summary_path: Path
    expected_condition_counts: Mapping[str, int]


DEFAULT_PUBLIC_SNAPSHOT_VALIDATION_SPECS = (
    PublicSnapshotValidationSpec(
        "Primary hosted gpt-5-mini snapshot",
        Path("artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl"),
        Path("artifacts/long-graph-v2/hosted-gpt5-mini-summary.json"),
        {
            "A1_AGENT_BASELINE": 72,
            "A4_FULL_DEFENSE": 72,
            "A8_CLASSIFIED_RELATION_GATE": 72,
            "A9_CALIBRATED_RELATION_GATE": 72,
            "A10_PRESERVATION_CALIBRATED_GATE": 72,
        },
    ),
    PublicSnapshotValidationSpec(
        "Cross-model gpt-4.1-mini snapshot",
        Path("artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl"),
        Path("artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-summary.json"),
        {
            "A8_CLASSIFIED_RELATION_GATE": 72,
            "A9_CALIBRATED_RELATION_GATE": 72,
            "A10_PRESERVATION_CALIBRATED_GATE": 72,
        },
    ),
)


def write_public_artifact_validation(
    tasks_path: Path,
    pages_path: Path,
    out_path: Path,
    specs: Sequence[PublicSnapshotValidationSpec] = DEFAULT_PUBLIC_SNAPSHOT_VALIDATION_SPECS,
) -> str:
    snapshots = [
        (
            spec,
            read_jsonl(spec.results_path),
            json.loads(spec.summary_path.read_text(encoding="utf-8")),
        )
        for spec in specs
    ]
    markdown = build_public_artifact_validation(
        load_tasks(tasks_path),
        load_pages(pages_path),
        tasks_path,
        pages_path,
        snapshots,
    )
    write_text(out_path, markdown)
    return markdown


def build_public_artifact_validation(
    tasks: Sequence[TaskCase],
    pages: Sequence[WebPage],
    tasks_path: Path,
    pages_path: Path,
    snapshots: Sequence[tuple[PublicSnapshotValidationSpec, Sequence[Mapping[str, Any]], Any]],
) -> str:
    task_ids = {task.id for task in tasks}
    page_ids = {page.id for page in pages}
    corpus_issues = _corpus_issues(tasks, pages, page_ids)
    snapshot_rows = [
        _snapshot_row(spec, rows, summary, task_ids, page_ids)
        for spec, rows, summary in snapshots
    ]
    issue_lines = _issue_lines(corpus_issues, snapshot_rows)

    lines = [
        "# Long-Graph v2 Public Artifact Validation",
        "",
        (
            "This deterministic report validates that the committed public v2 "
            "row snapshots are internally consistent, redacted, and referentially "
            "linked to the committed synthetic corpus."
        ),
        "",
        "## Sources",
        "",
        f"- Tasks: `{tasks_path}`",
        f"- Pages: `{pages_path}`",
    ]
    for spec, _rows, _summary in snapshots:
        lines.append(f"- Results: `{spec.results_path}`")
        lines.append(f"- Summary: `{spec.summary_path}`")
    lines.extend(
        [
            "",
            "## Corpus Checks",
            "",
            "| Check | Result | Detail |",
            "| --- | --- | --- |",
            f"| Task IDs unique | {_status(len(task_ids) == len(tasks))} | {len(tasks)} tasks |",
            f"| Page IDs unique | {_status(len(page_ids) == len(pages))} | {len(pages)} pages |",
            (
                "| Task required pages exist | "
                f"{_status(not corpus_issues)} | {_cell(_issue_summary(corpus_issues))} |"
            ),
            "",
            "## Snapshot Checks",
            "",
            (
                "| Snapshot | Rows | Summary match | Redaction check | "
                "Condition coverage | Unknown task IDs | Unknown page IDs |"
            ),
            "| --- | ---: | --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in snapshot_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(row["label"]),
                    str(row["rows"]),
                    _status(row["summary_match"]),
                    _status(row["redaction_safe"]),
                    _status(row["condition_coverage_ok"]),
                    str(row["unknown_task_count"]),
                    str(row["unknown_page_count"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Condition Counts",
            "",
            "| Snapshot | Condition | Expected rows | Observed rows |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for row in snapshot_rows:
        for condition, expected_count in row["expected_condition_counts"].items():
            observed_count = row["condition_counts"].get(condition, 0)
            lines.append(
                f"| {_cell(row['label'])} | `{condition}` | {expected_count} | {observed_count} |"
            )

    lines.extend(["", "## Issues", ""])
    if issue_lines:
        lines.extend(f"- {line}" for line in issue_lines)
    else:
        lines.append("- PASS: no validation issues found.")
    lines.append("")
    return "\n".join(lines)


def _corpus_issues(
    tasks: Sequence[TaskCase],
    pages: Sequence[WebPage],
    page_ids: set[str],
) -> list[str]:
    issues: list[str] = []
    duplicate_tasks = _duplicates(task.id for task in tasks)
    duplicate_pages = _duplicates(page.id for page in pages)
    if duplicate_tasks:
        issues.append(f"duplicate task IDs: {', '.join(duplicate_tasks)}")
    if duplicate_pages:
        issues.append(f"duplicate page IDs: {', '.join(duplicate_pages)}")
    missing_required_pages = sorted(
        {
            page_id
            for task in tasks
            for page_id in task.required_page_ids
            if page_id not in page_ids
        }
    )
    if missing_required_pages:
        issues.append(f"missing required pages: {', '.join(missing_required_pages)}")
    return issues


def _snapshot_row(
    spec: PublicSnapshotValidationSpec,
    rows: Sequence[Mapping[str, Any]],
    summary: Any,
    task_ids: set[str],
    page_ids: set[str],
) -> dict[str, Any]:
    condition_counts = Counter(str(row.get("condition")) for row in rows)
    unknown_task_ids = sorted({str(row.get("task_id")) for row in rows if row.get("task_id") not in task_ids})
    unknown_page_ids = _unknown_page_ids(rows, page_ids)
    expected_summary = summarize(rows)
    expected_condition_counts = dict(spec.expected_condition_counts)
    condition_coverage_ok = condition_counts == expected_condition_counts
    issues: list[str] = []
    if summary != expected_summary:
        issues.append("summary JSON does not match recomputed metrics")
    if not snapshot_is_public_safe(rows):
        issues.append("provider identifiers are not fully redacted")
    if not condition_coverage_ok:
        issues.append("condition counts differ from expected design")
    if unknown_task_ids:
        issues.append(f"unknown task IDs: {', '.join(unknown_task_ids)}")
    if unknown_page_ids:
        issues.append(f"unknown page IDs: {', '.join(unknown_page_ids)}")

    return {
        "label": spec.label,
        "rows": len(rows),
        "summary_match": summary == expected_summary,
        "redaction_safe": snapshot_is_public_safe(rows),
        "condition_coverage_ok": condition_coverage_ok,
        "unknown_task_count": len(unknown_task_ids),
        "unknown_page_count": len(unknown_page_ids),
        "condition_counts": dict(condition_counts),
        "expected_condition_counts": expected_condition_counts,
        "issues": issues,
    }


def _unknown_page_ids(rows: Sequence[Mapping[str, Any]], page_ids: set[str]) -> list[str]:
    unknown: set[str] = set()
    page_fields = ("cited_page_ids", "filtered_page_ids", "selected_page_ids", "visited_page_ids")
    for row in rows:
        for field in page_fields:
            value = row.get(field)
            if not isinstance(value, list):
                continue
            unknown.update(str(page_id) for page_id in value if page_id not in page_ids)
    return sorted(unknown)


def _duplicates(values: Sequence[str] | Any) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _issue_lines(corpus_issues: Sequence[str], snapshot_rows: Sequence[Mapping[str, Any]]) -> list[str]:
    issues = [f"Corpus: {issue}" for issue in corpus_issues]
    for row in snapshot_rows:
        for issue in row["issues"]:
            issues.append(f"{row['label']}: {issue}")
    return issues


def _issue_summary(issues: Sequence[str]) -> str:
    if not issues:
        return "all required page IDs resolve"
    return "; ".join(issues)


def _status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _cell(value: Any) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")
