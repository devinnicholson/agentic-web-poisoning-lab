from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence as RuntimeSequence
from math import sqrt
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from agentic_web_poisoning_lab.io import read_jsonl, write_text


def write_research_stats(results_path: Path, out_path: Path) -> str:
    rows = read_jsonl(results_path)
    markdown = build_research_stats(rows, results_path=results_path)
    write_text(out_path, markdown)
    return markdown


def build_research_stats(
    rows: Sequence[Mapping[str, Any]],
    results_path: Path | None = None,
) -> str:
    lines = ["# Research Statistics", ""]
    if results_path is not None:
        lines.extend([f"Source results: `{results_path}`", ""])

    lines.extend(_scope(rows))
    lines.extend(_condition_rates(rows))
    lines.extend(_attack_class_rates(rows))
    lines.extend(_defense_deltas(rows))
    lines.extend(_abstention_table(rows))
    lines.extend(_answer_confusion_table(rows))
    lines.extend(_false_non_abstain_examples(rows))
    lines.extend(_provider_reliability(rows))
    return "\n".join(lines).rstrip() + "\n"


def _scope(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    attack_rows = [row for row in rows if row.get("attack_type")]
    return [
        "## Scope",
        "",
        "| Field | Value |",
        "| --- | ---: |",
        f"| Rows | {len(rows)} |",
        f"| Attack rows | {len(attack_rows)} |",
        f"| Conditions | {len({str(row.get('condition')) for row in rows})} |",
        f"| Tasks | {len({str(row.get('task_id')) for row in rows})} |",
        "",
    ]


def _condition_rates(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    grouped = _group_by(rows, lambda row: str(row.get("condition")))
    lines = [
        "## Condition Rates With 95% Wilson Intervals",
        "",
        "| Condition | Rows | Attack rows | Accuracy | Attack success | Cited poisoned | Filtered poisoned | Provider error |",
        "| --- | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for condition, group in sorted(grouped.items()):
        attack_group = [row for row in group if row.get("attack_type")]
        lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    str(len(group)),
                    str(len(attack_group)),
                    _rate_cell(group, "answer_accuracy"),
                    _rate_cell(attack_group, "attack_success"),
                    _rate_cell(group, "cited_poisoned"),
                    _rate_cell(group, "filtered_poisoned"),
                    _rate_cell(group, "provider_error"),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _attack_class_rates(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    attack_rows = [row for row in rows if row.get("attack_type")]
    grouped = _group_by(attack_rows, lambda row: f"{row.get('attack_type')}|{row.get('condition')}")
    lines = [
        "## Attack-Class Rates",
        "",
        "| Attack type | Condition | Rows | Attack success | Cited poisoned | Filtered poisoned | Unsafe action |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for key, group in sorted(grouped.items()):
        attack_type, condition = key.split("|", 1)
        lines.append(
            "| "
            + " | ".join(
                [
                    attack_type,
                    condition,
                    str(len(group)),
                    _rate_cell(group, "attack_success"),
                    _rate_cell(group, "cited_poisoned"),
                    _rate_cell(group, "filtered_poisoned"),
                    _rate_cell(group, "unsafe_action"),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _defense_deltas(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    by_key = {
        (str(row.get("task_id")), str(row.get("condition"))): row
        for row in rows
        if row.get("attack_type")
    }
    baselines = [
        row
        for row in rows
        if row.get("attack_type") and row.get("condition") == "A1_AGENT_BASELINE"
    ]
    defense_conditions = sorted(
        {
            str(row.get("condition"))
            for row in rows
            if row.get("attack_type") and row.get("condition") != "A1_AGENT_BASELINE"
        }
    )

    lines = [
        "## Paired Defense Deltas vs A1 Baseline",
        "",
        "| Defense | Paired attacks | Attack-success reduction | Poisoned-citation reduction | Accuracy delta |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for defense in defense_conditions:
        pairs = [
            (baseline, by_key[(str(baseline.get("task_id")), defense)])
            for baseline in baselines
            if (str(baseline.get("task_id")), defense) in by_key
        ]
        lines.append(
            "| "
            + " | ".join(
                [
                    defense,
                    str(len(pairs)),
                    _delta_cell(pairs, "attack_success"),
                    _delta_cell(pairs, "cited_poisoned"),
                    _delta_cell(pairs, "answer_accuracy", higher_is_better=True),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _abstention_table(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    insufficient_rows = [row for row in rows if row.get("expected_answer") == "insufficient_evidence"]
    grouped = _group_by(insufficient_rows, lambda row: str(row.get("condition")))
    lines = [
        "## Abstention Calibration",
        "",
        "| Condition | Insufficient-evidence rows | Correct abstention | False non-abstain |",
        "| --- | ---: | --- | --- |",
    ]
    for condition, group in sorted(grouped.items()):
        false_non_abstain = [row for row in group if row.get("actual_answer") != "insufficient_evidence"]
        lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    str(len(group)),
                    _rate_cell(group, "answer_accuracy"),
                    _format_count_rate(len(false_non_abstain), len(group)),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _answer_confusion_table(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    answers = ["yes", "no", "insufficient_evidence"]
    grouped = _group_by(rows, lambda row: str(row.get("condition")))
    lines = [
        "## Answer Confusion Matrix",
        "",
        "| Condition | Expected | Actual yes | Actual no | Actual insufficient_evidence |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for condition, group in sorted(grouped.items()):
        for expected in answers:
            expected_group = [row for row in group if row.get("expected_answer") == expected]
            if not expected_group:
                continue
            counts = {
                actual: sum(1 for row in expected_group if row.get("actual_answer") == actual)
                for actual in answers
            }
            lines.append(
                "| "
                + " | ".join(
                    [
                        condition,
                        expected,
                        str(counts["yes"]),
                        str(counts["no"]),
                        str(counts["insufficient_evidence"]),
                    ]
                )
                + " |"
            )
    lines.append("")
    return lines


def _false_non_abstain_examples(
    rows: Sequence[Mapping[str, Any]],
    max_per_condition: int = 5,
) -> list[str]:
    examples = [
        row
        for row in rows
        if row.get("expected_answer") == "insufficient_evidence"
        and row.get("actual_answer") != "insufficient_evidence"
    ]
    lines = [
        "## False Non-Abstain Examples",
        "",
    ]
    if not examples:
        lines.extend(["No false non-abstain rows found.", ""])
        return lines

    lines.extend(
        [
            "| Condition | Task | Actual | Attack type | Cited poisoned | Cited pages |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    by_condition = _group_by(examples, lambda row: str(row.get("condition")))
    for condition, group in sorted(by_condition.items()):
        sorted_group = sorted(group, key=lambda item: str(item.get("task_id")))
        for row in sorted_group[:max_per_condition]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        condition,
                        str(row.get("task_id")),
                        str(row.get("actual_answer")),
                        str(row.get("attack_type") or "none"),
                        "yes" if _metric(row, "cited_poisoned") else "no",
                        _join_ids(row.get("cited_page_ids")),
                    ]
                )
                + " |"
            )
        if len(sorted_group) > max_per_condition:
            omitted = len(sorted_group) - max_per_condition
            lines.append(
                f"| {condition} | {omitted} additional rows omitted | ... | ... | ... | ... |"
            )
    lines.append("")
    return lines


def _provider_reliability(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    grouped = _group_by(rows, lambda row: str(row.get("condition")))
    lines = [
        "## Provider Reliability",
        "",
        "| Condition | Rows | Provider errors | Provider blocks | Total retries | Prompt tokens | Completion tokens |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for condition, group in sorted(grouped.items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    str(len(group)),
                    _rate_cell(group, "provider_error"),
                    _rate_cell(group, "provider_block"),
                    str(sum(_retry_count(row) for row in group)),
                    str(sum(_usage_value(row, "prompt_tokens") for row in group)),
                    str(sum(_usage_value(row, "completion_tokens") for row in group)),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _rate_cell(rows: Sequence[Mapping[str, Any]], metric_name: str) -> str:
    values = [_metric(row, metric_name) for row in rows]
    materialized = [value for value in values if value is not None]
    total = len(materialized)
    successes = sum(1 for value in materialized if value)
    return _format_count_rate(successes, total)


def _format_count_rate(successes: int, total: int) -> str:
    if total == 0:
        return "n/a"
    lower, upper = _wilson_interval(successes, total)
    rate = successes / total
    return f"{successes}/{total} ({rate * 100:.1f}%, 95% CI {lower * 100:.1f}-{upper * 100:.1f}%)"


def _delta_cell(
    pairs: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]],
    metric_name: str,
    higher_is_better: bool = False,
) -> str:
    if not pairs:
        return "n/a"
    baseline_rate = _pair_rate((baseline for baseline, _ in pairs), metric_name)
    defense_rate = _pair_rate((defense for _, defense in pairs), metric_name)
    delta = defense_rate - baseline_rate if higher_is_better else baseline_rate - defense_rate
    return f"{delta * 100:+.1f} pp ({baseline_rate * 100:.1f}% -> {defense_rate * 100:.1f}%)"


def _pair_rate(rows: Iterable[Mapping[str, Any]], metric_name: str) -> float:
    values = [_metric(row, metric_name) for row in rows]
    materialized = [value for value in values if value is not None]
    if not materialized:
        return 0.0
    return sum(1 for value in materialized if value) / len(materialized)


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return (0.0, 0.0)
    phat = successes / total
    denominator = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denominator
    half_width = (
        z
        * sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
        / denominator
    )
    return (max(0.0, center - half_width), min(1.0, center + half_width))


def _group_by(
    rows: Sequence[Mapping[str, Any]],
    key_fn: Any,
) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[key_fn(row)].append(row)
    return dict(grouped)


def _metric(row: Mapping[str, Any], name: str) -> Any:
    metrics = row.get("metrics")
    if isinstance(metrics, Mapping):
        return metrics.get(name)
    return None


def _metadata(row: Mapping[str, Any]) -> Mapping[str, Any]:
    metadata = row.get("provider_metadata")
    return metadata if isinstance(metadata, Mapping) else {}


def _retry_count(row: Mapping[str, Any]) -> int:
    value = _metadata(row).get("retry_count")
    return int(value) if isinstance(value, (int, float)) else 0


def _usage_value(row: Mapping[str, Any], key: str) -> int:
    usage = _metadata(row).get("usage")
    if not isinstance(usage, Mapping):
        return 0
    value = usage.get(key)
    return int(value) if isinstance(value, (int, float)) else 0


def _join_ids(value: Any) -> str:
    if isinstance(value, RuntimeSequence) and not isinstance(value, (str, bytes)):
        return ", ".join(str(item) for item in value) or "none"
    return "none"
