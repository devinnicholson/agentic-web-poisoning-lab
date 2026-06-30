from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_web_poisoning_lab.io import load_pages, read_jsonl, write_jsonl
from agentic_web_poisoning_lab.schema import WebPage


@dataclass(frozen=True)
class ResultRecord:
    row: Mapping[str, Any]
    source_path: Path | None = None
    source_line: int | None = None


def write_blind_audit_queue(
    results_paths: Sequence[Path],
    pages_path: Path,
    out_path: Path,
    out_key_path: Path | None = None,
    max_items: int = 96,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = _read_result_records(results_paths)
    pages = load_pages(pages_path)
    queue, key = build_blind_audit_artifacts(records, pages, max_items=max_items)
    write_jsonl(out_path, queue)
    if out_key_path is not None:
        write_jsonl(out_key_path, key)
    return queue, key


def build_blind_audit_artifacts(
    records: Sequence[ResultRecord | Mapping[str, Any]],
    pages: Sequence[WebPage],
    max_items: int = 96,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if max_items < 1:
        raise ValueError("max_items must be at least 1")

    normalized = [
        record if isinstance(record, ResultRecord) else ResultRecord(record)
        for record in records
    ]
    selected = _select_records(normalized, max_items=max_items)
    pages_by_id = {page.id: page for page in pages}
    queue = [_queue_item(record, pages_by_id) for record in selected]
    key = [_key_item(record) for record in selected]
    queue.sort(key=lambda item: str(item["audit_item_id"]))
    key.sort(key=lambda item: str(item["audit_item_id"]))
    return queue, key


def _read_result_records(results_paths: Sequence[Path]) -> list[ResultRecord]:
    records: list[ResultRecord] = []
    for path in results_paths:
        for line_index, row in enumerate(read_jsonl(path), start=1):
            records.append(ResultRecord(row=row, source_path=path, source_line=line_index))
    return records


def _select_records(records: Sequence[ResultRecord], max_items: int) -> list[ResultRecord]:
    if len(records) <= max_items:
        return sorted(records, key=_record_sort_key)

    groups: dict[tuple[str, str], list[ResultRecord]] = {}
    for record in records:
        groups.setdefault(_stratum(record.row), []).append(record)

    selected: list[ResultRecord] = []
    remainder: list[ResultRecord] = []
    strata = sorted(groups)
    base_quota = max_items // len(strata)
    extra = max_items % len(strata)

    for index, stratum in enumerate(strata):
        group = sorted(groups[stratum], key=_record_sort_key)
        quota = base_quota + (1 if index < extra else 0)
        selected.extend(group[:quota])
        remainder.extend(group[quota:])

    if len(selected) < max_items:
        selected.extend(sorted(remainder, key=_record_sort_key)[: max_items - len(selected)])
    return selected[:max_items]


def _stratum(row: Mapping[str, Any]) -> tuple[str, str]:
    metadata = row.get("provider_metadata") if isinstance(row.get("provider_metadata"), Mapping) else {}
    return (str(metadata.get("deployment") or "unknown_deployment"), str(row.get("condition") or "unknown_condition"))


def _record_sort_key(record: ResultRecord) -> tuple[str, str, str]:
    row = record.row
    return (
        _stable_digest(row),
        str(row.get("task_id") or ""),
        str(row.get("repeat_index") or 1),
    )


def _queue_item(record: ResultRecord, pages_by_id: Mapping[str, WebPage]) -> dict[str, Any]:
    row = record.row
    page_ids = _ordered_page_ids(row)
    page_refs = {page_id: f"P{index:02d}" for index, page_id in enumerate(page_ids, start=1)}
    answer = row.get("answer") if isinstance(row.get("answer"), Mapping) else {}
    return {
        "audit_item_id": _audit_item_id(row),
        "question": str(row.get("question") or ""),
        "response": {
            "answer_label": str(answer.get("answer") or row.get("actual_answer") or ""),
            "conclusion": _neutralize_blind_response_text(
                str(answer.get("conclusion") or ""),
                page_refs,
            ),
            "citation_refs": [page_refs[page_id] for page_id in _ids(row.get("cited_page_ids")) if page_id in page_refs],
            "refused": bool(answer.get("refused")) if "refused" in answer else None,
        },
        "page_evidence": [
            _page_evidence(page_id, page_refs[page_id], row, pages_by_id)
            for page_id in page_ids
            if page_id in pages_by_id
        ],
        "review_labels": {
            "answer_support": None,
            "source_selection": None,
            "citation_quality": None,
            "abstention_quality": None,
            "unsafe_action": None,
            "reviewer_confidence": None,
            "notes": None,
        },
    }


def _page_evidence(
    page_id: str,
    page_ref: str,
    row: Mapping[str, Any],
    pages_by_id: Mapping[str, WebPage],
) -> dict[str, Any]:
    page = pages_by_id[page_id]
    selected = set(_ids(row.get("selected_page_ids")))
    cited = set(_ids(row.get("cited_page_ids")))
    return {
        "page_ref": page_ref,
        "title": page.title,
        "source_type": page.source_type,
        "summary": _neutralize_page_ids(page.summary, {page_id: page_ref}),
        "model_interaction": {
            "visited": page_id in set(_ids(row.get("visited_page_ids"))),
            "selected": page_id in selected,
            "cited": page_id in cited,
        },
    }


def _key_item(record: ResultRecord) -> dict[str, Any]:
    row = record.row
    metadata = row.get("provider_metadata") if isinstance(row.get("provider_metadata"), Mapping) else {}
    metrics = row.get("metrics") if isinstance(row.get("metrics"), Mapping) else {}
    return {
        "audit_item_id": _audit_item_id(row),
        "source_path": str(record.source_path) if record.source_path is not None else None,
        "source_line": record.source_line,
        "run_id": row.get("run_id"),
        "task_id": row.get("task_id"),
        "condition": row.get("condition"),
        "repeat_index": row.get("repeat_index", 1),
        "deployment": metadata.get("deployment"),
        "model": metadata.get("model"),
        "expected_answer": row.get("expected_answer"),
        "actual_answer": row.get("actual_answer"),
        "attack_type": row.get("attack_type"),
        "attack_target_answer": row.get("attack_target_answer"),
        "metrics": {
            "answer_accuracy": metrics.get("answer_accuracy"),
            "attack_success": metrics.get("attack_success"),
            "cited_poisoned": metrics.get("cited_poisoned"),
            "stale_citation": metrics.get("stale_citation"),
            "unsafe_action": metrics.get("unsafe_action"),
            "refused": metrics.get("refused"),
        },
        "visited_page_ids": _ids(row.get("visited_page_ids")),
        "selected_page_ids": _ids(row.get("selected_page_ids")),
        "cited_page_ids": _ids(row.get("cited_page_ids")),
        "filtered_page_ids": _ids(row.get("filtered_page_ids")),
    }


def _ordered_page_ids(row: Mapping[str, Any]) -> list[str]:
    page_ids = _unique_ids(
        [
            *_ids(row.get("visited_page_ids")),
            *_ids(row.get("selected_page_ids")),
            *_ids(row.get("cited_page_ids")),
            *_ids(row.get("filtered_page_ids")),
        ]
    )
    row_digest = _stable_digest(row)
    return sorted(
        page_ids,
        key=lambda page_id: hashlib.sha256(f"{row_digest}|{page_id}".encode("utf-8")).hexdigest(),
    )


def _unique_ids(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _ids(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


def _audit_item_id(row: Mapping[str, Any]) -> str:
    return "blind_" + _stable_digest(row)[:16]


def _neutralize_page_ids(value: str, page_refs: Mapping[str, str]) -> str:
    neutralized = value
    for page_id, page_ref in sorted(page_refs.items(), key=lambda item: len(item[0]), reverse=True):
        neutralized = neutralized.replace(page_id, page_ref)
    return neutralized


def _neutralize_blind_response_text(value: str, page_refs: Mapping[str, str]) -> str:
    neutralized = _neutralize_page_ids(value, page_refs)
    replacements = {
        "Relation classifier gate:": "Evidence review note:",
        "classifier-predicted trusted evidence relation is": "selected trusted evidence is",
        "trusted evidence relation is": "selected trusted evidence is",
        "calibrated relation label of": "evidence note of",
        "calibrated-relation gate rules": "evidence-review rule",
        "preservation-calibrated sources": "trusted sources",
        "direct_support": "supporting evidence",
        "direct_refutation": "refuting evidence",
        "missing_validation": "missing validation evidence",
    }
    for needle, replacement in replacements.items():
        neutralized = neutralized.replace(needle, replacement)
    return neutralized


def _stable_digest(row: Mapping[str, Any]) -> str:
    metadata = row.get("provider_metadata") if isinstance(row.get("provider_metadata"), Mapping) else {}
    parts = [
        "lgv2-audit-v1",
        str(row.get("run_id") or ""),
        str(row.get("task_id") or ""),
        str(row.get("condition") or ""),
        str(row.get("repeat_index") or 1),
        str(metadata.get("deployment") or ""),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
