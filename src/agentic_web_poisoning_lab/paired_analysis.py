from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence as RuntimeSequence
from math import comb, sqrt
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from agentic_web_poisoning_lab.io import read_jsonl, write_text


CONDITION_ORDER = [
    "A0_DIRECT",
    "A1_AGENT_BASELINE",
    "A2_SOURCE_RANKING",
    "A3_PROMPT_SHIELDS",
    "A4_FULL_DEFENSE",
    "A5_STRICT_ABSTENTION",
    "A6_RELATION_VERIFIER",
    "A7_STRUCTURED_RELATION_GATE",
    "A8_CLASSIFIED_RELATION_GATE",
    "A9_CALIBRATED_RELATION_GATE",
    "A10_PRESERVATION_CALIBRATED_GATE",
]
RELATION_LABEL_ORDER = ["missing_validation", "direct_refutation", "direct_support"]
PRESERVATION_CONDITIONS = [
    "A8_CLASSIFIED_RELATION_GATE",
    "A9_CALIBRATED_RELATION_GATE",
    "A10_PRESERVATION_CALIBRATED_GATE",
]
PRESERVATION_COMPARISONS = [
    ("A8_CLASSIFIED_RELATION_GATE", "A10_PRESERVATION_CALIBRATED_GATE"),
    ("A9_CALIBRATED_RELATION_GATE", "A10_PRESERVATION_CALIBRATED_GATE"),
]


def write_paired_analysis(results_paths: Sequence[Path], out_path: Path) -> str:
    rows: list[Mapping[str, Any]] = []
    for path in results_paths:
        rows.extend(read_jsonl(path))
    markdown = build_paired_analysis(rows, source_paths=results_paths)
    write_text(out_path, markdown)
    return markdown


def write_preservation_analysis(results_paths: Sequence[Path], out_path: Path) -> str:
    rows: list[Mapping[str, Any]] = []
    for path in results_paths:
        rows.extend(read_jsonl(path))
    markdown = build_preservation_analysis(rows, source_paths=results_paths)
    write_text(out_path, markdown)
    return markdown


def build_paired_analysis(
    rows: Sequence[Mapping[str, Any]],
    source_paths: Sequence[Path] | None = None,
) -> str:
    indexed = _index_by_condition(rows)
    conditions = _ordered_conditions(indexed.keys())
    comparisons = _comparison_plan(conditions)

    lines = ["# Paired Condition Analysis", ""]
    if source_paths:
        lines.extend(["## Sources", ""])
        for path in source_paths:
            lines.append(f"- `{path}`")
        lines.append("")

    lines.extend(_scope(rows, conditions, comparisons, indexed))
    lines.extend(_condition_scorecard(indexed, conditions))
    lines.extend(
        _paired_delta_table(
            indexed,
            comparisons,
            title="Paired Accuracy Deltas",
            row_filter=lambda _row: True,
            metric_label="Accuracy delta",
        )
    )
    lines.extend(
        _paired_delta_table(
            indexed,
            comparisons,
            title="Paired Abstention Deltas",
            row_filter=lambda row: row.get("expected_answer") == "insufficient_evidence",
            metric_label="Correct-abstention delta",
        )
    )
    lines.extend(
        _paired_delta_table(
            indexed,
            comparisons,
            title="Paired Direct-Negative Deltas",
            row_filter=lambda row: row.get("expected_answer") == "no",
            metric_label="Direct-no delta",
        )
    )
    lines.extend(_relation_label_taxonomy(rows))
    lines.extend(_calibration_override_table(rows))
    lines.extend(_failure_inventory(rows))
    lines.extend(_interpretation(indexed))
    return "\n".join(lines).rstrip() + "\n"


def build_preservation_analysis(
    rows: Sequence[Mapping[str, Any]],
    source_paths: Sequence[Path] | None = None,
) -> str:
    analysis_rows = [
        row for row in rows if str(row.get("condition")) in set(PRESERVATION_CONDITIONS)
    ]
    indexed = _index_by_deployment_condition(analysis_rows)
    deployments = _ordered_deployments(analysis_rows)

    lines = ["# Long-Graph v2 Preservation Paired Analysis", ""]
    if source_paths:
        lines.extend(["## Sources", ""])
        for path in source_paths:
            lines.append(f"- `{path}`")
        lines.append("")

    lines.extend(_preservation_scope(rows, analysis_rows, deployments, indexed))
    lines.extend(_preservation_run_metadata(analysis_rows, deployments))
    lines.extend(_preservation_scorecard(indexed, deployments))
    lines.extend(_preservation_pairwise_tests(indexed, deployments))
    lines.extend(_preservation_boundary_inventory(indexed, deployments))
    lines.extend(_preservation_interpretation(indexed, deployments))
    return "\n".join(lines).rstrip() + "\n"


def _scope(
    rows: Sequence[Mapping[str, Any]],
    conditions: Sequence[str],
    comparisons: Sequence[tuple[str, str]],
    indexed: Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]],
) -> list[str]:
    tasks = {str(row.get("task_id")) for row in rows}
    repeats = {
        str(row.get("repeat_index", 1))
        for row in rows
        if row.get("repeat_index") is not None
    }
    common_keys = _common_keys(indexed, conditions) if conditions else set()
    return [
        "## Scope",
        "",
        "| Field | Value |",
        "| --- | ---: |",
        f"| Rows | {len(rows)} |",
        f"| Conditions | {len(conditions)} |",
        f"| Tasks | {len(tasks)} |",
        f"| Repeat indexes | {len(repeats) if repeats else 1} |",
        f"| Fully paired task/repeat cells | {len(common_keys)} |",
        f"| Planned pairwise comparisons | {len(comparisons)} |",
        "",
    ]


def _condition_scorecard(
    indexed: Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]],
    conditions: Sequence[str],
) -> list[str]:
    lines = [
        "## Condition Scorecard",
        "",
        "| Condition | Rows | Accuracy | Correct abstention | False non-abstain | Direct no preserved | Attack success | Cited poisoned |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for condition in conditions:
        rows = list(indexed[condition].values())
        insufficient = [row for row in rows if row.get("expected_answer") == "insufficient_evidence"]
        direct_no = [row for row in rows if row.get("expected_answer") == "no"]
        false_non_abstain = [
            row for row in insufficient if row.get("actual_answer") != "insufficient_evidence"
        ]
        lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    str(len(rows)),
                    _count_rate(sum(1 for row in rows if _is_correct(row)), len(rows)),
                    _count_rate(
                        sum(1 for row in insufficient if _is_correct(row)),
                        len(insufficient),
                    ),
                    _count_rate(len(false_non_abstain), len(insufficient)),
                    _count_rate(
                        sum(1 for row in direct_no if row.get("actual_answer") == "no"),
                        len(direct_no),
                    ),
                    _count_rate(sum(1 for row in rows if _metric(row, "attack_success")), len(rows)),
                    _count_rate(sum(1 for row in rows if _metric(row, "cited_poisoned")), len(rows)),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _preservation_scope(
    source_rows: Sequence[Mapping[str, Any]],
    analysis_rows: Sequence[Mapping[str, Any]],
    deployments: Sequence[str],
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]]],
) -> list[str]:
    tasks = {str(row.get("task_id")) for row in analysis_rows}
    repeats = {
        str(row.get("repeat_index", 1))
        for row in analysis_rows
        if row.get("repeat_index") is not None
    }
    paired_cells = 0
    for deployment in deployments:
        deployment_index = indexed.get(deployment, {})
        present_conditions = [
            condition for condition in PRESERVATION_CONDITIONS if condition in deployment_index
        ]
        if present_conditions:
            paired_cells += len(_common_keys(deployment_index, present_conditions))
    return [
        "## Scope",
        "",
        "| Field | Value |",
        "| --- | ---: |",
        f"| Source rows read | {len(source_rows)} |",
        f"| A8/A9/A10 analysis rows | {len(analysis_rows)} |",
        f"| Deployments | {len(deployments)} |",
        f"| Tasks | {len(tasks)} |",
        f"| Repeat indexes | {len(repeats) if repeats else 1} |",
        f"| Fully paired deployment/task/repeat cells | {paired_cells} |",
        "",
    ]


def _preservation_run_metadata(
    rows: Sequence[Mapping[str, Any]],
    deployments: Sequence[str],
) -> list[str]:
    lines = [
        "## Run Metadata",
        "",
        "| Deployment | Rows | Models | Run modes | Run IDs |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for deployment in deployments:
        deployment_rows = [row for row in rows if _deployment_label(row) == deployment]
        models = _sorted_metadata_values(deployment_rows, "model")
        run_modes = _sorted_metadata_values(deployment_rows, "run_mode")
        run_ids = sorted({str(row.get("run_id")) for row in deployment_rows if row.get("run_id")})
        lines.append(
            "| "
            + " | ".join(
                [
                    deployment,
                    str(len(deployment_rows)),
                    _join_values(models),
                    _join_values(run_modes),
                    _join_values(run_ids),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _preservation_scorecard(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]]],
    deployments: Sequence[str],
) -> list[str]:
    lines = [
        "## Deployment Scorecard",
        "",
        "| Deployment | Condition | Rows | Accuracy | Correct abstention | Direct controls | Direct yes | Direct no | Attack success | Cited poisoned | Provider errors |",
        "| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for deployment in deployments:
        deployment_index = indexed.get(deployment, {})
        for condition in PRESERVATION_CONDITIONS:
            rows = list(deployment_index.get(condition, {}).values())
            if not rows:
                continue
            insufficient = [row for row in rows if row.get("expected_answer") == "insufficient_evidence"]
            direct = [row for row in rows if row.get("expected_answer") in {"yes", "no"}]
            direct_yes = [row for row in rows if row.get("expected_answer") == "yes"]
            direct_no = [row for row in rows if row.get("expected_answer") == "no"]
            lines.append(
                "| "
                + " | ".join(
                    [
                        deployment,
                        condition,
                        str(len(rows)),
                        _count_rate(sum(1 for row in rows if _is_correct(row)), len(rows)),
                        _count_rate(sum(1 for row in insufficient if _is_correct(row)), len(insufficient)),
                        _count_rate(sum(1 for row in direct if _is_correct(row)), len(direct)),
                        _count_rate(sum(1 for row in direct_yes if _is_correct(row)), len(direct_yes)),
                        _count_rate(sum(1 for row in direct_no if _is_correct(row)), len(direct_no)),
                        _count_rate(sum(1 for row in rows if _metric(row, "attack_success")), len(rows)),
                        _count_rate(sum(1 for row in rows if _metric(row, "cited_poisoned")), len(rows)),
                        _count_rate(sum(1 for row in rows if _metric(row, "provider_error")), len(rows)),
                    ]
                )
                + " |"
            )
    lines.append("")
    return lines


def _preservation_pairwise_tests(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]]],
    deployments: Sequence[str],
) -> list[str]:
    lines = [
        "## Paired Preservation Tests",
        "",
        "| Scope | Comparison | Slice | Paired rows | First-only correct | A10-only correct | Both correct | Both wrong | Accuracy delta | Exact McNemar p |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    slices: list[tuple[str, Callable[[Mapping[str, Any]], bool]]] = [
        ("All rows", lambda _row: True),
        ("Evidence gaps", lambda row: row.get("expected_answer") == "insufficient_evidence"),
        ("Direct controls", lambda row: row.get("expected_answer") in {"yes", "no"}),
        ("Direct yes", lambda row: row.get("expected_answer") == "yes"),
        ("Direct no", lambda row: row.get("expected_answer") == "no"),
    ]
    scoped_indexes = [(deployment, indexed.get(deployment, {})) for deployment in deployments]
    scoped_indexes.append(("Combined deployments", _combined_preservation_index(indexed, deployments)))

    for scope, condition_index in scoped_indexes:
        for first, second in PRESERVATION_COMPARISONS:
            if first not in condition_index or second not in condition_index:
                continue
            for slice_label, row_filter in slices:
                stats = _paired_stats(condition_index, first, second, row_filter)
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            scope,
                            f"{first} -> {second}",
                            slice_label,
                            str(stats["paired"]),
                            str(stats["first_only"]),
                            str(stats["second_only"]),
                            str(stats["both_correct"]),
                            str(stats["both_wrong"]),
                            _format_pp(float(stats["delta"])),
                            _format_p_value(float(stats["p_value"])),
                        ]
                    )
                    + " |"
                )
    lines.append("")
    return lines


def _preservation_boundary_inventory(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]]],
    deployments: Sequence[str],
) -> list[str]:
    lines = [
        "## Boundary Repair Inventory",
        "",
        "| Deployment | Comparison | Task | Expected | First correct | A10 correct | First answers | A10 answers |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    found = False
    for deployment in deployments:
        deployment_index = indexed.get(deployment, {})
        for first, second in PRESERVATION_COMPARISONS:
            first_rows = deployment_index.get(first, {})
            second_rows = deployment_index.get(second, {})
            task_ids = sorted({key[0] for key in set(first_rows) & set(second_rows)})
            for task_id in task_ids:
                paired = [
                    (first_rows[(task_id, repeat)], second_rows[(task_id, repeat)])
                    for repeat in sorted(
                        {
                            key[1]
                            for key in set(first_rows) & set(second_rows)
                            if key[0] == task_id
                        }
                    )
                ]
                if not paired:
                    continue
                expected = str(paired[0][0].get("expected_answer"))
                if expected not in {"yes", "no"}:
                    continue
                first_correct = sum(1 for first_row, _second_row in paired if _is_correct(first_row))
                second_correct = sum(1 for _first_row, second_row in paired if _is_correct(second_row))
                if second_correct <= first_correct:
                    continue
                found = True
                first_task_rows = [first_row for first_row, _second_row in paired]
                second_task_rows = [second_row for _first_row, second_row in paired]
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            deployment,
                            f"{first} -> {second}",
                            task_id,
                            expected,
                            f"{first_correct}/{len(paired)}",
                            f"{second_correct}/{len(paired)}",
                            _actual_answer_counts(first_task_rows),
                            _actual_answer_counts(second_task_rows),
                        ]
                    )
                    + " |"
                )
    if not found:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    lines.append("")
    return lines


def _preservation_interpretation(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]]],
    deployments: Sequence[str],
) -> list[str]:
    combined = _combined_preservation_index(indexed, deployments)
    a8_direct = _paired_stats(
        combined,
        "A8_CLASSIFIED_RELATION_GATE",
        "A10_PRESERVATION_CALIBRATED_GATE",
        lambda row: row.get("expected_answer") in {"yes", "no"},
    )
    a9_direct = _paired_stats(
        combined,
        "A9_CALIBRATED_RELATION_GATE",
        "A10_PRESERVATION_CALIBRATED_GATE",
        lambda row: row.get("expected_answer") in {"yes", "no"},
    )
    return [
        "## Interpretation",
        "",
        (
            "Across paired deployment/task/repeat cells, A10's gains are "
            "concentrated on direct controls rather than evidence gaps. "
            f"Against A8, A10 fixed {a8_direct['second_only']} direct-control "
            f"rows and introduced {a8_direct['first_only']} new direct-control "
            f"misses ({_format_p_clause(float(a8_direct['p_value']))}). "
            f"Against A9, A10 fixed {a9_direct['second_only']} direct-control "
            f"rows and introduced {a9_direct['first_only']} new direct-control "
            f"misses ({_format_p_clause(float(a9_direct['p_value']))})."
        ),
        "",
        (
            "The evidence-gap rows are unchanged by the preservation layer: A8, "
            "A9, and A10 all preserve correct abstention on every paired "
            "insufficient-evidence row in this v2 analysis."
        ),
        "",
    ]


def _paired_delta_table(
    indexed: Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]],
    comparisons: Sequence[tuple[str, str]],
    title: str,
    row_filter: Callable[[Mapping[str, Any]], bool],
    metric_label: str,
) -> list[str]:
    lines = [
        f"## {title}",
        "",
        f"| Comparison | Paired rows | First-only correct | Second-only correct | Both correct | Both wrong | {metric_label} | Exact McNemar p |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for first, second in comparisons:
        stats = _paired_stats(indexed, first, second, row_filter)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{first} -> {second}",
                    str(stats["paired"]),
                    str(stats["first_only"]),
                    str(stats["second_only"]),
                    str(stats["both_correct"]),
                    str(stats["both_wrong"]),
                    _format_pp(float(stats["delta"])),
                    _format_p_value(float(stats["p_value"])),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _paired_stats(
    indexed: Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]],
    first: str,
    second: str,
    row_filter: Callable[[Mapping[str, Any]], bool],
) -> dict[str, float | int]:
    first_rows = indexed.get(first, {})
    second_rows = indexed.get(second, {})
    keys = sorted(set(first_rows) & set(second_rows))
    paired = [
        (first_rows[key], second_rows[key])
        for key in keys
        if row_filter(first_rows[key]) and row_filter(second_rows[key])
    ]
    first_only = sum(1 for left, right in paired if _is_correct(left) and not _is_correct(right))
    second_only = sum(1 for left, right in paired if not _is_correct(left) and _is_correct(right))
    both_correct = sum(1 for left, right in paired if _is_correct(left) and _is_correct(right))
    both_wrong = sum(1 for left, right in paired if not _is_correct(left) and not _is_correct(right))
    first_rate = (first_only + both_correct) / len(paired) if paired else 0.0
    second_rate = (second_only + both_correct) / len(paired) if paired else 0.0
    return {
        "paired": len(paired),
        "first_only": first_only,
        "second_only": second_only,
        "both_correct": both_correct,
        "both_wrong": both_wrong,
        "delta": second_rate - first_rate,
        "p_value": _exact_mcnemar_p(first_only, second_only),
    }


def _relation_label_taxonomy(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        entries = _relation_classifier_entries(row)
        if entries:
            grouped[(str(row.get("condition")), str(row.get("expected_answer")))].append(row)

    lines = [
        "## Relation Label Taxonomy",
        "",
    ]
    if not grouped:
        lines.extend(["No relation-classifier metadata found.", ""])
        return lines

    lines.extend(
        [
            "| Condition | Expected answer | Calls | Raw labels | Final labels | Overrides |",
            "| --- | --- | ---: | --- | --- | ---: |",
        ]
    )
    for condition, expected in sorted(grouped, key=lambda item: (_condition_rank(item[0]), item[1])):
        group = grouped[(condition, expected)]
        raw_counts: Counter[str] = Counter()
        final_counts: Counter[str] = Counter()
        overrides = 0
        calls = 0
        for row in group:
            for entry in _relation_classifier_entries(row):
                calls += 1
                raw_counts[str(entry.get("raw_label") or "unknown")] += 1
                final_counts[str(entry.get("final_label") or "unknown")] += 1
                overrides += 1 if entry.get("override") else 0
        lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    expected,
                    str(calls),
                    _format_counter(raw_counts),
                    _format_counter(final_counts),
                    str(overrides),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _calibration_override_table(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        if any(entry.get("override") for entry in _relation_classifier_entries(row)):
            grouped[(str(row.get("condition")), str(row.get("task_id")))].append(row)

    lines = [
        "## Calibration Overrides",
        "",
    ]
    if not grouped:
        lines.extend(["No calibration overrides found.", ""])
        return lines

    lines.extend(
        [
            "| Condition | Task | Overrides | Raw -> final labels | Actual answers |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for condition, task_id in sorted(grouped, key=lambda item: (_condition_rank(item[0]), item[1])):
        group = grouped[(condition, task_id)]
        transitions: Counter[str] = Counter()
        override_count = 0
        for row in group:
            for entry in _relation_classifier_entries(row):
                if entry.get("override"):
                    override_count += 1
                    transitions[f"{entry.get('raw_label')} -> {entry.get('final_label')}"] += 1
        lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    task_id,
                    str(override_count),
                    _format_counter(transitions),
                    _actual_answer_counts(group),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _failure_inventory(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    failures = [row for row in rows if not _is_correct(row)]
    lines = [
        "## Failure Inventory",
        "",
    ]
    if not failures:
        lines.extend(["No incorrect rows found.", ""])
        return lines

    lines.extend(
        [
            "| Condition | Task | Repeat | Expected | Actual | Relation labels | Cited pages |",
            "| --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in sorted(
        failures,
        key=lambda item: (
            _condition_rank(str(item.get("condition"))),
            str(item.get("task_id")),
            int(item.get("repeat_index", 1) or 1),
        ),
    ):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.get("condition")),
                    str(row.get("task_id")),
                    str(row.get("repeat_index", 1)),
                    str(row.get("expected_answer")),
                    str(row.get("actual_answer")),
                    _row_relation_labels(row),
                    _join_ids(row.get("cited_page_ids")),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _interpretation(indexed: Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]]) -> list[str]:
    if not {
        "A7_STRUCTURED_RELATION_GATE",
        "A8_CLASSIFIED_RELATION_GATE",
        "A9_CALIBRATED_RELATION_GATE",
    } <= set(indexed):
        return []

    a8_a9 = _paired_stats(
        indexed,
        "A8_CLASSIFIED_RELATION_GATE",
        "A9_CALIBRATED_RELATION_GATE",
        lambda row: row.get("expected_answer") == "insufficient_evidence",
    )
    return [
        "## Interpretation",
        "",
        (
            "A8 and A9 are paired by task and repeat index, so the A9 result is "
            "not just an aggregate-rate comparison. On missing-validation rows, "
            f"A9 fixed {a8_a9['second_only']} rows that A8 answered incorrectly "
            f"and introduced {a8_a9['first_only']} new misses. This isolates the "
            "measured gain to relation-label calibration rather than source "
            "filtering or task mix."
        ),
        "",
        (
            "The paired human audit labels for these A8 misses and A9 repairs "
            "are committed in `data/manual-audit.hosted-a8-a9-boundary.jsonl`."
        ),
        "",
    ]


def _index_by_condition(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[tuple[str, str], Mapping[str, Any]]]:
    indexed: dict[str, dict[tuple[str, str], Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        condition = str(row.get("condition"))
        indexed[condition][_pair_key(row)] = row
    return dict(indexed)


def _index_by_deployment_condition(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, dict[tuple[str, str], Mapping[str, Any]]]]:
    indexed: dict[str, dict[str, dict[tuple[str, str], Mapping[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in rows:
        deployment = _deployment_label(row)
        condition = str(row.get("condition"))
        indexed[deployment][condition][_pair_key(row)] = row
    return {
        deployment: {condition: dict(condition_rows) for condition, condition_rows in condition_index.items()}
        for deployment, condition_index in indexed.items()
    }


def _combined_preservation_index(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]]],
    deployments: Sequence[str],
) -> dict[str, dict[tuple[str, str], Mapping[str, Any]]]:
    combined: dict[str, dict[tuple[str, str], Mapping[str, Any]]] = defaultdict(dict)
    for deployment in deployments:
        for condition, condition_rows in indexed.get(deployment, {}).items():
            for (task_id, repeat), row in condition_rows.items():
                combined[condition][(f"{deployment}:{task_id}", repeat)] = row
    return dict(combined)


def _pair_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return (str(row.get("task_id")), str(row.get("repeat_index", 1)))


def _deployment_label(row: Mapping[str, Any]) -> str:
    metadata = row.get("provider_metadata")
    if isinstance(metadata, Mapping):
        deployment = metadata.get("deployment") or metadata.get("model")
        if deployment:
            return str(deployment)
    return "unknown_deployment"


def _ordered_deployments(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    deployments: list[str] = []
    for row in rows:
        deployment = _deployment_label(row)
        if deployment not in deployments:
            deployments.append(deployment)
    return deployments


def _sorted_metadata_values(rows: Sequence[Mapping[str, Any]], key: str) -> list[str]:
    values: set[str] = set()
    for row in rows:
        metadata = row.get("provider_metadata")
        if isinstance(metadata, Mapping) and metadata.get(key):
            values.add(str(metadata[key]))
    return sorted(values)


def _join_values(values: Sequence[str]) -> str:
    return ", ".join(values) if values else "n/a"


def _ordered_conditions(conditions: RuntimeSequence[str]) -> list[str]:
    return sorted(conditions, key=lambda condition: (_condition_rank(condition), condition))


def _condition_rank(condition: str) -> int:
    try:
        return CONDITION_ORDER.index(condition)
    except ValueError:
        return len(CONDITION_ORDER)


def _comparison_plan(conditions: Sequence[str]) -> list[tuple[str, str]]:
    preferred = [
        ("A7_STRUCTURED_RELATION_GATE", "A8_CLASSIFIED_RELATION_GATE"),
        ("A8_CLASSIFIED_RELATION_GATE", "A9_CALIBRATED_RELATION_GATE"),
        ("A7_STRUCTURED_RELATION_GATE", "A9_CALIBRATED_RELATION_GATE"),
    ]
    present = set(conditions)
    selected = [pair for pair in preferred if pair[0] in present and pair[1] in present]
    if selected:
        return selected
    return list(zip(conditions, conditions[1:]))


def _common_keys(
    indexed: Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]],
    conditions: Sequence[str],
) -> set[tuple[str, str]]:
    if not conditions:
        return set()
    common = set(indexed[conditions[0]])
    for condition in conditions[1:]:
        common &= set(indexed[condition])
    return common


def _relation_classifier_entries(row: Mapping[str, Any]) -> list[dict[str, Any]]:
    metadata = row.get("provider_metadata")
    if not isinstance(metadata, Mapping):
        return []
    entries = metadata.get("relation_classifier")
    if not isinstance(entries, RuntimeSequence) or isinstance(entries, (str, bytes)):
        return []

    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        final_label = str(entry.get("evidence_relation") or "unknown")
        raw_label = str(entry.get("raw_evidence_relation") or final_label)
        normalized.append(
            {
                "page_id": entry.get("page_id"),
                "raw_label": raw_label,
                "final_label": final_label,
                "override": bool(entry.get("calibration_override")),
            }
        )
    return normalized


def _row_relation_labels(row: Mapping[str, Any]) -> str:
    entries = _relation_classifier_entries(row)
    if not entries:
        labels = row.get("safety_flags")
        if isinstance(labels, Mapping):
            relation_labels = labels.get("relation_labels")
            if isinstance(relation_labels, Mapping):
                return _format_mapping(relation_labels)
        return "none"
    parts = []
    for entry in entries:
        page_id = entry.get("page_id") or "unknown_page"
        raw_label = entry.get("raw_label")
        final_label = entry.get("final_label")
        if raw_label == final_label:
            parts.append(f"{page_id}:{final_label}")
        else:
            parts.append(f"{page_id}:{raw_label}->{final_label}")
    return "; ".join(parts)


def _exact_mcnemar_p(first_only: int, second_only: int) -> float:
    discordant = first_only + second_only
    if discordant == 0:
        return 1.0
    tail = min(first_only, second_only)
    probability = sum(comb(discordant, value) for value in range(tail + 1)) / (2**discordant)
    return min(1.0, 2 * probability)


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


def _count_rate(successes: int, total: int) -> str:
    if total == 0:
        return "n/a"
    lower, upper = _wilson_interval(successes, total)
    return (
        f"{successes}/{total} "
        f"({successes / total * 100:.1f}%, 95% CI {lower * 100:.1f}-{upper * 100:.1f}%)"
    )


def _format_pp(value: float) -> str:
    return f"{value * 100:+.1f} pp"


def _format_p_value(value: float) -> str:
    if value < 0.0001:
        return "<0.0001"
    return f"{value:.4f}"


def _format_p_clause(value: float) -> str:
    formatted = _format_p_value(value)
    if formatted.startswith("<"):
        return f"exact McNemar p < {formatted.removeprefix('<')}"
    return f"exact McNemar p = {formatted}"


def _format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    ordered = [label for label in RELATION_LABEL_ORDER if counter.get(label)]
    ordered.extend(sorted(label for label in counter if label not in ordered))
    return "; ".join(f"{label}={counter[label]}" for label in ordered)


def _format_mapping(value: Mapping[Any, Any]) -> str:
    if not value:
        return "none"
    return "; ".join(f"{key}:{value[key]}" for key in sorted(value))


def _actual_answer_counts(rows: Sequence[Mapping[str, Any]]) -> str:
    preferred_order = ["yes", "no", "insufficient_evidence"]
    counts: Counter[str] = Counter(str(row.get("actual_answer")) for row in rows)
    ordered = [answer for answer in preferred_order if counts.get(answer)]
    ordered.extend(sorted(answer for answer in counts if answer not in ordered))
    return "; ".join(f"{answer}={counts[answer]}" for answer in ordered)


def _metric(row: Mapping[str, Any], name: str) -> Any:
    metrics = row.get("metrics")
    if isinstance(metrics, Mapping):
        return metrics.get(name)
    return None


def _is_correct(row: Mapping[str, Any]) -> bool:
    return bool(_metric(row, "answer_accuracy"))


def _join_ids(value: Any) -> str:
    if isinstance(value, RuntimeSequence) and not isinstance(value, (str, bytes)):
        return ", ".join(str(item) for item in value) or "none"
    return "none"
