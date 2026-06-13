from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_web_poisoning_lab.io import read_jsonl, write_text
from agentic_web_poisoning_lab.metrics import summarize


def write_markdown_report(results_path: Path, out_path: Path) -> str:
    rows = read_jsonl(results_path)
    markdown = build_markdown_report(rows, results_path=results_path)
    write_text(out_path, markdown)
    return markdown


def build_markdown_report(
    rows: Sequence[Mapping[str, Any]],
    results_path: Path | None = None,
) -> str:
    lines = ["# Agentic Web Poisoning Report", ""]
    if results_path is not None:
        lines.extend([f"Source results: `{results_path}`", ""])

    lines.extend(_executive_summary(rows))
    lines.extend(_condition_table(summarize(rows)))
    lines.extend(_attack_breakdown(rows))
    lines.extend(_notable_examples(rows))
    return "\n".join(lines).rstrip() + "\n"


def _executive_summary(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    attack_rows = [row for row in rows if row.get("attack_type")]
    return [
        "## Executive Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Result rows | {len(rows)} |",
        f"| Attack rows | {len(attack_rows)} |",
        f"| Overall answer accuracy | {_format_percent(_rate(_metric(row, 'answer_accuracy') for row in rows))} |",
        f"| Overall attack success | {_format_percent(_rate(_metric(row, 'attack_success') for row in attack_rows))} |",
        f"| Overall cited poisoned rate | {_format_percent(_rate(_metric(row, 'cited_poisoned') for row in rows))} |",
        "",
    ]


def _condition_table(summary_rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = [
        "## Condition Scorecard",
        "",
        "| Condition | Cases | Attack cases | Accuracy | Attack success | Unsafe action | Cited poisoned | Stale citation | Filtered poisoned | Refused | Avg latency | Est. cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["condition"]),
                    str(row["total_cases"]),
                    str(row["attack_cases"]),
                    _format_percent(row["answer_accuracy"]),
                    _format_percent(row["attack_success_rate"]),
                    _format_percent(row["unsafe_action_rate"]),
                    _format_percent(row["cited_poisoned_rate"]),
                    _format_percent(row["stale_citation_rate"]),
                    _format_percent(row["filtered_poisoned_rate"]),
                    _format_percent(row["refused_rate"]),
                    f"{row['avg_latency_ms']:.2f} ms",
                    f"${float(row['estimated_cost_usd']):.6f}",
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _attack_breakdown(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in rows:
        attack_type = row.get("attack_type")
        if not attack_type:
            continue
        key = (str(attack_type), str(row["condition"]))
        grouped.setdefault(key, []).append(row)

    lines = [
        "## Attack-Class Breakdown",
        "",
        "| Attack type | Condition | Rows | Attack success | Cited poisoned | Unsafe action |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for (attack_type, condition), group in sorted(grouped.items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    attack_type,
                    condition,
                    str(len(group)),
                    _format_percent(_rate(_metric(row, "attack_success") for row in group)),
                    _format_percent(_rate(_metric(row, "cited_poisoned") for row in group)),
                    _format_percent(_rate(_metric(row, "unsafe_action") for row in group)),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _notable_examples(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = ["## Notable Examples", ""]
    attack_success = _first(rows, lambda row: _metric(row, "attack_success"))
    clean_defense = _first(
        rows,
        lambda row: row.get("condition") == "A4_FULL_DEFENSE"
        and row.get("attack_type")
        and not _metric(row, "attack_success")
        and not _metric(row, "cited_poisoned"),
    )

    if attack_success:
        lines.extend(_example_block("Baseline attack success", attack_success))
    if clean_defense:
        lines.extend(_example_block("Clean defended trace", clean_defense))
    if not attack_success and not clean_defense:
        lines.append("No notable examples found.")
    lines.append("")
    return lines


def _example_block(title: str, row: Mapping[str, Any]) -> list[str]:
    answer = row.get("answer") if isinstance(row.get("answer"), Mapping) else {}
    return [
        f"### {title}",
        "",
        f"- Task: `{row.get('task_id')}` in `{row.get('condition')}`",
        f"- Question: {row.get('question')}",
        f"- Expected vs actual: `{row.get('expected_answer')}` -> `{row.get('actual_answer')}`",
        f"- Attack type: `{row.get('attack_type')}`",
        f"- Visited pages: `{', '.join(row.get('visited_page_ids') or []) or 'none'}`",
        f"- Filtered pages: `{', '.join(row.get('filtered_page_ids') or []) or 'none'}`",
        f"- Cited pages: `{', '.join(row.get('cited_page_ids') or []) or 'none'}`",
        f"- Answer summary: {answer.get('conclusion') or ''}",
        "",
    ]


def _first(rows: Sequence[Mapping[str, Any]], predicate: Any) -> Mapping[str, Any] | None:
    for row in rows:
        if predicate(row):
            return row
    return None


def _metric(row: Mapping[str, Any], name: str) -> Any:
    metrics = row.get("metrics")
    if isinstance(metrics, Mapping):
        return metrics.get(name)
    return None


def _rate(values: Any) -> float | None:
    materialized = list(values)
    if not materialized:
        return None
    return round(sum(1 for value in materialized if value) / len(materialized), 4)


def _format_percent(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.1f}%"
