from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_web_poisoning_lab.blind_audit import audit_item_id_for_row
from agentic_web_poisoning_lab.io import read_jsonl, write_text


@dataclass(frozen=True)
class BlindAuditValidationSpec:
    queue_path: Path
    key_path: Path
    results_paths: tuple[Path, ...]


DEFAULT_BLIND_AUDIT_VALIDATION_SPEC = BlindAuditValidationSpec(
    queue_path=Path("artifacts/long-graph-v2/blind-audit-queue.jsonl"),
    key_path=Path("artifacts/long-graph-v2/blind-audit-key.jsonl"),
    results_paths=(
        Path("artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl"),
        Path("artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl"),
    ),
)

FORBIDDEN_QUEUE_KEYS = {
    "actual_answer",
    "attack_target_answer",
    "attack_type",
    "condition",
    "deployment",
    "expected_answer",
    "filtered_page_ids",
    "metrics",
    "model",
    "provider_metadata",
    "run_id",
    "safety_flags",
    "source_line",
    "source_path",
    "task_id",
}

FORBIDDEN_QUEUE_SUBSTRINGS = (
    "A1_AGENT_BASELINE",
    "A4_FULL_DEFENSE",
    "A8_CLASSIFIED_RELATION_GATE",
    "A9_CALIBRATED_RELATION_GATE",
    "A10_PRESERVATION_CALIBRATED_GATE",
    "task_long_v2_",
    "page_v2_",
    '"actual_answer"',
    '"attack_target_answer"',
    '"condition"',
    '"deployment"',
    '"expected_answer"',
    '"metrics"',
    '"model"',
    '"provider_metadata"',
    '"run_id"',
    '"safety_flags"',
    '"task_id"',
    '"trust_label"',
    '"is_poisoned"',
    '"supports_tasks"',
    "Relation classifier gate",
    "classifier-predicted",
    "direct_support",
    "direct_refutation",
    "missing_validation",
    "calibrated-relation gate",
    "preservation-calibrated",
)

REVIEW_LABEL_FIELDS = {
    "abstention_quality",
    "answer_support",
    "citation_quality",
    "notes",
    "reviewer_confidence",
    "source_selection",
    "unsafe_action",
}

PAGE_REF_RE = re.compile(r"^P\d{2}$")


def write_blind_audit_validation(
    out_path: Path,
    spec: BlindAuditValidationSpec = DEFAULT_BLIND_AUDIT_VALIDATION_SPEC,
) -> str:
    queue = read_jsonl(spec.queue_path)
    key = read_jsonl(spec.key_path)
    source_rows = _source_rows(spec.results_paths)
    markdown = build_blind_audit_validation(queue, key, source_rows, spec)
    write_text(out_path, markdown)
    return markdown


def build_blind_audit_validation(
    queue: Sequence[Mapping[str, Any]],
    key: Sequence[Mapping[str, Any]],
    source_rows: Sequence[tuple[Path, int, Mapping[str, Any]]],
    spec: BlindAuditValidationSpec = DEFAULT_BLIND_AUDIT_VALIDATION_SPEC,
) -> str:
    expected_ids = {
        audit_item_id_for_row(row): {"source_path": str(path), "source_line": line}
        for path, line, row in source_rows
    }
    queue_ids = [str(row.get("audit_item_id")) for row in queue]
    key_ids = [str(row.get("audit_item_id")) for row in key]
    queue_id_set = set(queue_ids)
    key_id_set = set(key_ids)
    expected_id_set = set(expected_ids)

    forbidden_keys = _forbidden_keys(queue)
    forbidden_substrings = _forbidden_substrings(queue)
    label_issues = _label_issues(queue)
    page_ref_issues = _page_ref_issues(queue)
    key_source_issues = _key_source_issues(key, expected_ids)
    queue_duplicates = _duplicates(queue_ids)
    key_duplicates = _duplicates(key_ids)

    checks = [
        (
            "Queue row count",
            len(queue) == len(source_rows),
            f"{len(queue)} queue rows; {len(source_rows)} source rows",
        ),
        (
            "Key row count",
            len(key) == len(source_rows),
            f"{len(key)} key rows; {len(source_rows)} source rows",
        ),
        (
            "Queue audit IDs unique",
            not queue_duplicates,
            _issue_summary(queue_duplicates, "all queue audit IDs unique"),
        ),
        (
            "Key audit IDs unique",
            not key_duplicates,
            _issue_summary(key_duplicates, "all key audit IDs unique"),
        ),
        (
            "Queue/key ID sets match",
            queue_id_set == key_id_set,
            _set_diff_detail(queue_id_set, key_id_set, "queue", "key"),
        ),
        (
            "Key covers source rows",
            key_id_set == expected_id_set,
            _set_diff_detail(key_id_set, expected_id_set, "key", "source"),
        ),
        (
            "Key source pointers match source rows",
            not key_source_issues,
            _issue_summary(key_source_issues, "all key source pointers match"),
        ),
        (
            "Reviewer labels are empty",
            not label_issues,
            _issue_summary(label_issues, "all review label slots are null"),
        ),
        (
            "Page aliases are local and cited refs resolve",
            not page_ref_issues,
            _issue_summary(page_ref_issues, "all page aliases and citations resolve"),
        ),
        (
            "Queue does not expose key-only fields",
            not forbidden_keys,
            _issue_summary(forbidden_keys, "no forbidden structured keys found"),
        ),
        (
            "Forbidden leakage scan",
            not forbidden_substrings,
            _issue_summary(forbidden_substrings, "no configured leakage strings found"),
        ),
    ]
    issue_lines = [
        f"{name}: {detail}"
        for name, ok, detail in checks
        if not ok
    ]

    lines = [
        "# Long-Graph v2 Blind Audit Validation",
        "",
        (
            "This deterministic report validates that the committed blinded audit "
            "queue is aligned with the public row snapshots while keeping the "
            "reviewer-facing packet free of configured condition, task, page, "
            "metric, and provider leaks."
        ),
        "",
        "## Sources",
        "",
        f"- Blind queue: `{spec.queue_path}`",
        f"- Unblinding key: `{spec.key_path}`",
    ]
    for path in spec.results_paths:
        lines.append(f"- Source rows: `{path}`")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Result | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for name, ok, detail in checks:
        lines.append(f"| {_cell(name)} | {_status(ok)} | {_cell(detail)} |")

    lines.extend(
        [
            "",
            "## Coverage",
            "",
            "| Item | Count |",
            "| --- | ---: |",
            f"| Source rows | {len(source_rows)} |",
            f"| Blind queue rows | {len(queue)} |",
            f"| Unblinding key rows | {len(key)} |",
            f"| Queue unique audit IDs | {len(queue_id_set)} |",
            f"| Key unique audit IDs | {len(key_id_set)} |",
            "",
            "## Issues",
            "",
        ]
    )
    if issue_lines:
        lines.extend(f"- {line}" for line in issue_lines)
    else:
        lines.append("- PASS: no validation issues found.")
    lines.append("")
    return "\n".join(lines)


def _source_rows(results_paths: Sequence[Path]) -> list[tuple[Path, int, Mapping[str, Any]]]:
    rows: list[tuple[Path, int, Mapping[str, Any]]] = []
    for path in results_paths:
        for line, row in enumerate(read_jsonl(path), start=1):
            rows.append((path, line, row))
    return rows


def _forbidden_keys(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    found: set[str] = set()
    for row in rows:
        _collect_forbidden_keys(row, found)
    return sorted(found)


def _collect_forbidden_keys(value: Any, found: set[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in FORBIDDEN_QUEUE_KEYS:
                found.add(str(key))
            _collect_forbidden_keys(item, found)
    elif isinstance(value, list):
        for item in value:
            _collect_forbidden_keys(item, found)


def _forbidden_substrings(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    text = "\n".join(json.dumps(row, sort_keys=True) for row in rows).lower()
    return sorted(
        needle
        for needle in FORBIDDEN_QUEUE_SUBSTRINGS
        if needle.lower() in text
    )


def _label_issues(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    issues: list[str] = []
    for index, row in enumerate(rows, start=1):
        audit_id = str(row.get("audit_item_id") or f"row-{index}")
        labels = row.get("review_labels")
        if not isinstance(labels, Mapping):
            issues.append(f"{audit_id}: missing review_labels object")
            continue
        fields = set(str(key) for key in labels)
        if fields != REVIEW_LABEL_FIELDS:
            missing = sorted(REVIEW_LABEL_FIELDS - fields)
            extra = sorted(fields - REVIEW_LABEL_FIELDS)
            issues.append(f"{audit_id}: label fields missing={missing} extra={extra}")
        filled = sorted(str(key) for key, value in labels.items() if value is not None)
        if filled:
            issues.append(f"{audit_id}: prefilled label fields {filled}")
    return issues


def _page_ref_issues(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    issues: list[str] = []
    for index, row in enumerate(rows, start=1):
        audit_id = str(row.get("audit_item_id") or f"row-{index}")
        pages = row.get("page_evidence")
        if not isinstance(pages, list):
            issues.append(f"{audit_id}: missing page_evidence list")
            continue
        page_refs = [str(page.get("page_ref")) for page in pages if isinstance(page, Mapping)]
        invalid_refs = sorted(ref for ref in page_refs if not PAGE_REF_RE.match(ref))
        duplicate_refs = _duplicates(page_refs)
        citation_refs = _citation_refs(row)
        unresolved_citations = sorted(ref for ref in citation_refs if ref not in set(page_refs))
        if invalid_refs:
            issues.append(f"{audit_id}: invalid page refs {invalid_refs}")
        if duplicate_refs:
            issues.append(f"{audit_id}: duplicate page refs {duplicate_refs}")
        if unresolved_citations:
            issues.append(f"{audit_id}: unresolved citation refs {unresolved_citations}")
    return issues


def _citation_refs(row: Mapping[str, Any]) -> list[str]:
    response = row.get("response")
    if not isinstance(response, Mapping):
        return []
    refs = response.get("citation_refs")
    if not isinstance(refs, list):
        return []
    return [str(ref) for ref in refs]


def _key_source_issues(
    key: Sequence[Mapping[str, Any]],
    expected_ids: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    issues: list[str] = []
    for row in key:
        audit_id = str(row.get("audit_item_id"))
        expected = expected_ids.get(audit_id)
        if expected is None:
            issues.append(f"{audit_id}: key row is not derived from source rows")
            continue
        if row.get("source_path") != expected["source_path"]:
            issues.append(f"{audit_id}: source_path mismatch")
        if row.get("source_line") != expected["source_line"]:
            issues.append(f"{audit_id}: source_line mismatch")
    return issues


def _duplicates(values: Sequence[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _set_diff_detail(left: set[str], right: set[str], left_label: str, right_label: str) -> str:
    missing_from_left = sorted(right - left)
    missing_from_right = sorted(left - right)
    if not missing_from_left and not missing_from_right:
        return f"{left_label} and {right_label} ID sets match"
    parts = []
    if missing_from_left:
        parts.append(f"missing from {left_label}: {', '.join(missing_from_left[:10])}")
    if missing_from_right:
        parts.append(f"missing from {right_label}: {', '.join(missing_from_right[:10])}")
    return "; ".join(parts)


def _issue_summary(issues: Sequence[str], pass_message: str) -> str:
    if not issues:
        return pass_message
    if len(issues) <= 5:
        return "; ".join(issues)
    return "; ".join(issues[:5]) + f"; plus {len(issues) - 5} more"


def _status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _cell(value: Any) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")
