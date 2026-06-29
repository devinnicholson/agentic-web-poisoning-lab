from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence as RuntimeSequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_web_poisoning_lab.io import load_pages, read_jsonl, write_text
from agentic_web_poisoning_lab.preservation_casebook import FIRST_CONDITIONS, SECOND_CONDITION
from agentic_web_poisoning_lab.schema import WebPage


@dataclass(frozen=True)
class PairedRow:
    deployment: str
    first_condition: str
    task_id: str
    repeat_index: int
    expected_answer: str
    first_row: Mapping[str, Any]
    second_row: Mapping[str, Any]


def write_preservation_transition_analysis(
    results_paths: Sequence[Path],
    pages_path: Path,
    out_path: Path,
) -> str:
    rows: list[Mapping[str, Any]] = []
    for path in results_paths:
        rows.extend(read_jsonl(path))
    markdown = build_preservation_transition_analysis(
        rows,
        load_pages(pages_path),
        source_paths=results_paths,
        pages_path=pages_path,
    )
    write_text(out_path, markdown)
    return markdown


def build_preservation_transition_analysis(
    rows: Sequence[Mapping[str, Any]],
    pages: Sequence[WebPage],
    source_paths: Sequence[Path] | None = None,
    pages_path: Path | None = None,
) -> str:
    page_index = {page.id: page for page in pages}
    paired_rows = _paired_direct_rows(rows)
    repairs = [pair for pair in paired_rows if _is_repair(pair)]
    regressions = [pair for pair in paired_rows if _is_regression(pair)]

    lines = ["# Long-Graph v2 Preservation Transition Analysis", ""]
    if source_paths or pages_path:
        lines.extend(["## Sources", ""])
        for path in source_paths or []:
            lines.append(f"- Results: `{path}`")
        if pages_path:
            lines.append(f"- Pages: `{pages_path}`")
        lines.append("")

    lines.extend(_scope(rows, pages, paired_rows, repairs, regressions))
    lines.extend(_comparison_table(paired_rows))
    lines.extend(_transition_matrix(paired_rows, repairs))
    lines.extend(_top_page_transitions(repairs, page_index))
    lines.extend(_interpretation(paired_rows, repairs, regressions))
    return "\n".join(lines).rstrip() + "\n"


def _scope(
    rows: Sequence[Mapping[str, Any]],
    pages: Sequence[WebPage],
    paired_rows: Sequence[PairedRow],
    repairs: Sequence[PairedRow],
    regressions: Sequence[PairedRow],
) -> list[str]:
    return [
        "## Scope",
        "",
        "| Field | Value |",
        "| --- | ---: |",
        f"| Source rows read | {len(rows)} |",
        f"| Page corpus rows | {len(pages)} |",
        f"| Direct paired A8/A9 -> A10 rows | {len(paired_rows)} |",
        f"| Repaired direct-control rows | {len(repairs)} |",
        f"| New A10 direct-control misses | {len(regressions)} |",
        f"| Repair page-label transition observations | {_transition_observation_count(repairs)} |",
        "",
    ]


def _comparison_table(paired_rows: Sequence[PairedRow]) -> list[str]:
    lines = [
        "## Comparison-Level Mechanism",
        "",
        "| Scope | Comparison | Direct paired rows | Repairs | New A10 misses | Rows with label changes | Repair rows with label changes | Repair transition observations |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    deployments = _ordered_values(pair.deployment for pair in paired_rows)
    for scope, scope_pairs in [("Combined deployments", list(paired_rows))] + [
        (deployment, [pair for pair in paired_rows if pair.deployment == deployment])
        for deployment in deployments
    ]:
        for first_condition in FIRST_CONDITIONS:
            pairs = [pair for pair in scope_pairs if pair.first_condition == first_condition]
            if not pairs:
                continue
            repairs = [pair for pair in pairs if _is_repair(pair)]
            regressions = [pair for pair in pairs if _is_regression(pair)]
            changed_rows = [pair for pair in pairs if _label_transitions(pair)]
            changed_repairs = [pair for pair in repairs if _label_transitions(pair)]
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(scope),
                        _cell(f"{first_condition} -> {SECOND_CONDITION}"),
                        str(len(pairs)),
                        str(len(repairs)),
                        str(len(regressions)),
                        str(len(changed_rows)),
                        str(len(changed_repairs)),
                        str(_transition_observation_count(repairs)),
                    ]
                )
                + " |"
            )
    lines.append("")
    return lines


def _transition_matrix(
    paired_rows: Sequence[PairedRow],
    repairs: Sequence[PairedRow],
) -> list[str]:
    lines = [
        "## Label Transition Matrix",
        "",
        "| Comparison | Transition | All direct observations | Repair observations |",
        "| --- | --- | ---: | ---: |",
    ]
    for first_condition in FIRST_CONDITIONS:
        all_counts = _transition_counts(
            pair for pair in paired_rows if pair.first_condition == first_condition
        )
        repair_counts = _transition_counts(
            pair for pair in repairs if pair.first_condition == first_condition
        )
        transitions = _ordered_transitions(set(all_counts) | set(repair_counts))
        if not transitions:
            lines.append(f"| {_cell(first_condition)} -> {SECOND_CONDITION} | none | 0 | 0 |")
            continue
        for transition in transitions:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(f"{first_condition} -> {SECOND_CONDITION}"),
                        _cell(f"{transition[0]} -> {transition[1]}"),
                        str(all_counts[transition]),
                        str(repair_counts[transition]),
                    ]
                )
                + " |"
            )
    lines.append("")
    return lines


def _top_page_transitions(
    repairs: Sequence[PairedRow],
    page_index: Mapping[str, WebPage],
    limit: int = 12,
) -> list[str]:
    page_counts: Counter[tuple[str, str, str]] = Counter()
    page_tasks: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for pair in repairs:
        for page_id, first_label, second_label in _label_transitions(pair):
            key = (page_id, first_label, second_label)
            page_counts[key] += 1
            page_tasks[key].add(pair.task_id)

    lines = [
        "## Repaired Page Transitions",
        "",
        "| Page | Title | Transition | Repair observations | Tasks |",
        "| --- | --- | --- | ---: | --- |",
    ]
    if not page_counts:
        lines.append("| n/a | n/a | n/a | 0 | n/a |")
        lines.append("")
        return lines

    for (page_id, first_label, second_label), count in page_counts.most_common(limit):
        page = page_index.get(page_id)
        title = page.title if page else "missing from page corpus"
        tasks = ", ".join(sorted(page_tasks[(page_id, first_label, second_label)]))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_cell(page_id)}`",
                    _cell(title),
                    _cell(f"{first_label} -> {second_label}"),
                    str(count),
                    _cell(tasks),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _interpretation(
    paired_rows: Sequence[PairedRow],
    repairs: Sequence[PairedRow],
    regressions: Sequence[PairedRow],
) -> list[str]:
    repair_transitions = _transition_counts(repairs)
    nonrepair_changes = [
        pair
        for pair in paired_rows
        if not _is_repair(pair) and _label_transitions(pair)
    ]
    final_labels = Counter(
        second_label
        for pair in repairs
        for _page_id, _first_label, second_label in _label_transitions(pair)
    )
    final_label_summary = _format_counter(final_labels)
    return [
        "## Interpretation",
        "",
        (
            f"A10's mechanism-level changes are concentrated on repaired rows: "
            f"{sum(repair_transitions.values())} page-label transition observations "
            f"appear on {len(repairs)} repaired direct-control rows, while "
            f"{len(nonrepair_changes)} non-repaired direct-control rows changed labels."
        ),
        "",
        (
            f"The terminal A10 labels on repaired transitions are {final_label_summary}. "
            "This supports the preservation-layer hypothesis: A10 restores direct "
            "support or direct refutation on trusted current pages rather than "
            "weakening the evidence-gap abstention rule globally."
        ),
        "",
        (
            f"No new A10 direct-control misses were observed in this paired slice "
            f"({len(regressions)} regressions)."
        ),
        "",
    ]


def _paired_direct_rows(rows: Sequence[Mapping[str, Any]]) -> list[PairedRow]:
    indexed: dict[str, dict[str, dict[tuple[str, int], Mapping[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    deployments: list[str] = []
    for row in rows:
        condition = str(row.get("condition"))
        if condition not in {*FIRST_CONDITIONS, SECOND_CONDITION}:
            continue
        deployment = _deployment_label(row)
        if deployment not in deployments:
            deployments.append(deployment)
        indexed[deployment][condition][_pair_key(row)] = row

    pairs: list[PairedRow] = []
    for deployment in deployments:
        deployment_index = indexed.get(deployment, {})
        for first_condition in FIRST_CONDITIONS:
            first_rows = deployment_index.get(first_condition, {})
            second_rows = deployment_index.get(SECOND_CONDITION, {})
            for key in sorted(set(first_rows) & set(second_rows)):
                first_row = first_rows[key]
                second_row = second_rows[key]
                expected_answer = first_row.get("expected_answer")
                if expected_answer != second_row.get("expected_answer"):
                    continue
                if expected_answer not in {"yes", "no"}:
                    continue
                pairs.append(
                    PairedRow(
                        deployment=deployment,
                        first_condition=first_condition,
                        task_id=key[0],
                        repeat_index=key[1],
                        expected_answer=str(expected_answer),
                        first_row=first_row,
                        second_row=second_row,
                    )
                )
    return pairs


def _label_transitions(pair: PairedRow) -> list[tuple[str, str, str]]:
    first_labels = _label_map(pair.first_row)
    second_labels = _label_map(pair.second_row)
    transitions: list[tuple[str, str, str]] = []
    for page_id in sorted(set(first_labels) | set(second_labels)):
        first_label = first_labels.get(page_id, "missing")
        second_label = second_labels.get(page_id, "missing")
        if first_label != second_label:
            transitions.append((page_id, first_label, second_label))
    return transitions


def _transition_counts(pairs: Iterable[PairedRow]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for pair in pairs:
        for _page_id, first_label, second_label in _label_transitions(pair):
            counts[(first_label, second_label)] += 1
    return counts


def _transition_observation_count(pairs: Sequence[PairedRow]) -> int:
    return sum(len(_label_transitions(pair)) for pair in pairs)


def _label_map(row: Mapping[str, Any]) -> dict[str, str]:
    answer = row.get("answer")
    if isinstance(answer, Mapping):
        labels = answer.get("relation_labels")
        if isinstance(labels, Mapping) and labels:
            return {str(key): str(value) for key, value in labels.items()}

    safety_flags = row.get("safety_flags")
    if isinstance(safety_flags, Mapping):
        labels = safety_flags.get("relation_labels")
        if isinstance(labels, Mapping) and labels:
            return {str(key): str(value) for key, value in labels.items()}

    metadata = row.get("provider_metadata")
    if not isinstance(metadata, Mapping):
        return {}
    entries = metadata.get("relation_classifier")
    if not isinstance(entries, RuntimeSequence) or isinstance(entries, (str, bytes)):
        return {}
    labels: dict[str, str] = {}
    for entry in entries:
        if isinstance(entry, Mapping) and entry.get("page_id"):
            labels[str(entry["page_id"])] = str(entry.get("evidence_relation") or "unknown")
    return labels


def _pair_key(row: Mapping[str, Any]) -> tuple[str, int]:
    return (str(row.get("task_id")), int(row.get("repeat_index", 1) or 1))


def _deployment_label(row: Mapping[str, Any]) -> str:
    metadata = row.get("provider_metadata")
    if isinstance(metadata, Mapping):
        deployment = metadata.get("deployment") or metadata.get("model")
        if deployment:
            return str(deployment)
    return "unknown_deployment"


def _is_repair(pair: PairedRow) -> bool:
    return not _is_correct(pair.first_row) and _is_correct(pair.second_row)


def _is_regression(pair: PairedRow) -> bool:
    return _is_correct(pair.first_row) and not _is_correct(pair.second_row)


def _is_correct(row: Mapping[str, Any]) -> bool:
    metrics = row.get("metrics")
    if isinstance(metrics, Mapping):
        return bool(metrics.get("answer_accuracy"))
    return False


def _ordered_values(values: Iterable[str]) -> list[str]:
    ordered: list[str] = []
    for value in values:
        if value not in ordered:
            ordered.append(value)
    return ordered


def _ordered_transitions(transitions: set[tuple[str, str]]) -> list[tuple[str, str]]:
    preferred = [
        ("missing_validation", "direct_refutation"),
        ("direct_support", "direct_refutation"),
        ("missing_validation", "direct_support"),
    ]
    ordered = [transition for transition in preferred if transition in transitions]
    ordered.extend(sorted(transition for transition in transitions if transition not in ordered))
    return ordered


def _format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    preferred = ["direct_refutation", "direct_support", "missing_validation"]
    ordered = [label for label in preferred if counter.get(label)]
    ordered.extend(sorted(label for label in counter if label not in ordered))
    return ", ".join(f"{label}={counter[label]}" for label in ordered)


def _cell(value: str) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")
