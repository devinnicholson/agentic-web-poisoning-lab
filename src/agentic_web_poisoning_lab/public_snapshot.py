from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_web_poisoning_lab.io import read_jsonl, write_jsonl
from agentic_web_poisoning_lab.metrics import summarize


REDACTED_VALUE = "redacted_for_public_snapshot"
REDACTED_PROVIDER_METADATA_KEYS = frozenset(
    {
        "endpoint_host",
        "response_id",
        "system_fingerprint",
    }
)


def write_public_snapshot(
    results_path: Path,
    out_results_path: Path,
    out_summary_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [sanitize_result_row(row) for row in read_jsonl(results_path)]
    write_jsonl(out_results_path, rows)
    summary = summarize(rows)
    out_summary_path.parent.mkdir(parents=True, exist_ok=True)
    out_summary_path.write_text(_json_summary(summary), encoding="utf-8")
    return rows, summary


def sanitize_result_row(row: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = deepcopy(dict(row))
    provider_metadata = sanitized.get("provider_metadata")
    redacted_paths: list[str] = []

    if isinstance(provider_metadata, dict):
        for key in sorted(REDACTED_PROVIDER_METADATA_KEYS):
            if key in provider_metadata:
                provider_metadata[key] = REDACTED_VALUE
                redacted_paths.append(f"provider_metadata.{key}")

    if redacted_paths:
        sanitized["public_snapshot_redactions"] = redacted_paths

    return sanitized


def snapshot_is_public_safe(rows: Sequence[Mapping[str, Any]]) -> bool:
    return all(_row_is_public_safe(row) for row in rows)


def _row_is_public_safe(row: Mapping[str, Any]) -> bool:
    provider_metadata = row.get("provider_metadata")
    if not isinstance(provider_metadata, dict):
        return True
    for key in REDACTED_PROVIDER_METADATA_KEYS:
        value = provider_metadata.get(key)
        if value not in {None, REDACTED_VALUE}:
            return False
    return True


def _json_summary(summary: Mapping[str, Any]) -> str:
    import json

    return json.dumps(summary, indent=2, sort_keys=True) + "\n"
