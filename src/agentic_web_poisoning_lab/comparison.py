from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_web_poisoning_lab.io import read_jsonl, write_text


def write_comparison_report(local_path: Path, hosted_path: Path, out_path: Path) -> str:
    local_rows = read_jsonl(local_path)
    hosted_rows = read_jsonl(hosted_path)
    markdown = build_comparison_report(local_rows, hosted_rows, local_path, hosted_path)
    write_text(out_path, markdown)
    return markdown


def build_comparison_report(
    local_rows: Sequence[Mapping[str, Any]],
    hosted_rows: Sequence[Mapping[str, Any]],
    local_path: Path | None = None,
    hosted_path: Path | None = None,
) -> str:
    pairs = _paired_rows(local_rows, hosted_rows)
    lines = ["# Hosted vs Local Comparison", ""]
    if local_path is not None:
        lines.append(f"Local source: `{local_path}`")
    if hosted_path is not None:
        lines.append(f"Hosted source: `{hosted_path}`")
    if local_path is not None or hosted_path is not None:
        lines.append("")

    lines.extend(_summary(pairs, hosted_rows))
    lines.extend(_delta_table(pairs))
    lines.extend(_risk_table(pairs))
    lines.extend(_provider_table(hosted_rows))
    return "\n".join(lines).rstrip() + "\n"


def _paired_rows(
    local_rows: Sequence[Mapping[str, Any]],
    hosted_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Mapping[str, Any]]]:
    local_by_key = {
        (str(row.get("task_id")), str(row.get("condition"))): row
        for row in local_rows
    }
    pairs: list[dict[str, Mapping[str, Any]]] = []
    for hosted in hosted_rows:
        key = (str(hosted.get("task_id")), str(hosted.get("condition")))
        local = local_by_key.get(key)
        if local is not None:
            pairs.append({"local": local, "hosted": hosted})
    return sorted(
        pairs,
        key=lambda pair: (
            str(pair["hosted"].get("condition")),
            str(pair["hosted"].get("task_id")),
        ),
    )


def _summary(
    pairs: Sequence[Mapping[str, Mapping[str, Any]]],
    hosted_rows: Sequence[Mapping[str, Any]],
) -> list[str]:
    hosted_attack_rows = [row for row in hosted_rows if row.get("attack_type")]
    recovered = [
        pair
        for pair in pairs
        if _metric(pair["local"], "attack_success") and not _metric(pair["hosted"], "attack_success")
    ]
    hosted_poisoned_citations = [row for row in hosted_rows if _metric(row, "cited_poisoned")]
    provider_errors = [row for row in hosted_rows if _metric(row, "provider_error")]
    provider_blocks = [row for row in hosted_rows if _metric(row, "provider_block")]
    return [
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Paired rows | {len(pairs)} |",
        f"| Hosted rows | {len(hosted_rows)} |",
        f"| Hosted attack rows | {len(hosted_attack_rows)} |",
        f"| Local attack successes recovered by hosted model | {len(recovered)} |",
        f"| Hosted poisoned-citation rows | {len(hosted_poisoned_citations)} |",
        f"| Hosted provider errors | {len(provider_errors)} |",
        f"| Hosted provider blocks | {len(provider_blocks)} |",
        "",
    ]


def _delta_table(pairs: Sequence[Mapping[str, Mapping[str, Any]]]) -> list[str]:
    lines = [
        "## Answer Deltas",
        "",
        "| Task | Attack | Condition | Expected | Local actual | Hosted actual | Local accurate | Hosted accurate |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for pair in pairs:
        local = pair["local"]
        hosted = pair["hosted"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(hosted.get("task_id")),
                    str(hosted.get("attack_type") or "none"),
                    str(hosted.get("condition")),
                    f"`{hosted.get('expected_answer')}`",
                    f"`{local.get('actual_answer')}`",
                    f"`{hosted.get('actual_answer')}`",
                    _check(_metric(local, "answer_accuracy")),
                    _check(_metric(hosted, "answer_accuracy")),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _risk_table(pairs: Sequence[Mapping[str, Mapping[str, Any]]]) -> list[str]:
    risky = [
        pair
        for pair in pairs
        if pair["hosted"].get("attack_type")
        or _metric(pair["hosted"], "cited_poisoned")
        or _metric(pair["local"], "attack_success")
        or _metric(pair["hosted"], "provider_error")
    ]
    lines = [
        "## Risk Deltas",
        "",
        "| Task | Condition | Local attack success | Hosted attack success | Local cited poisoned | Hosted cited poisoned | Hosted filtered poisoned |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for pair in risky:
        local = pair["local"]
        hosted = pair["hosted"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(hosted.get("task_id")),
                    str(hosted.get("condition")),
                    _check(_metric(local, "attack_success")),
                    _check(_metric(hosted, "attack_success")),
                    _check(_metric(local, "cited_poisoned")),
                    _check(_metric(hosted, "cited_poisoned")),
                    _check(_metric(hosted, "filtered_poisoned")),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _provider_table(hosted_rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = [
        "## Provider Outcomes",
        "",
        "| Condition | Task | Model | Finish reason | Retries | Provider block | Provider error | Latency |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted(hosted_rows, key=lambda item: (str(item.get("condition")), str(item.get("task_id")))):
        metadata = row.get("provider_metadata") if isinstance(row.get("provider_metadata"), Mapping) else {}
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.get("condition")),
                    str(row.get("task_id")),
                    str(metadata.get("model") or "n/a"),
                    str(metadata.get("finish_reason") or "n/a"),
                    str(metadata.get("retry_count") if metadata.get("retry_count") is not None else "n/a"),
                    _check(_metric(row, "provider_block")),
                    _check(_metric(row, "provider_error")),
                    f"{float(row.get('latency_ms') or 0):.0f} ms",
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _metric(row: Mapping[str, Any], name: str) -> Any:
    metrics = row.get("metrics")
    if isinstance(metrics, Mapping):
        return metrics.get(name)
    return None


def _check(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "n/a"
