from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence as RuntimeSequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_web_poisoning_lab.io import load_pages, read_jsonl, write_text
from agentic_web_poisoning_lab.schema import WebPage


FIRST_CONDITIONS = (
    "A8_CLASSIFIED_RELATION_GATE",
    "A9_CALIBRATED_RELATION_GATE",
)
SECOND_CONDITION = "A10_PRESERVATION_CALIBRATED_GATE"


@dataclass(frozen=True)
class RepairCase:
    deployment: str
    first_condition: str
    task_id: str
    repeat_index: int
    expected_answer: str
    question: str
    first_row: Mapping[str, Any]
    second_row: Mapping[str, Any]
    paired_rows: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]]


def write_preservation_casebook(
    results_paths: Sequence[Path],
    pages_path: Path,
    out_path: Path,
    max_cases: int = 20,
) -> str:
    rows: list[Mapping[str, Any]] = []
    for path in results_paths:
        rows.extend(read_jsonl(path))
    markdown = build_preservation_casebook(
        rows,
        load_pages(pages_path),
        source_paths=results_paths,
        pages_path=pages_path,
        max_cases=max_cases,
    )
    write_text(out_path, markdown)
    return markdown


def build_preservation_casebook(
    rows: Sequence[Mapping[str, Any]],
    pages: Sequence[WebPage],
    source_paths: Sequence[Path] | None = None,
    pages_path: Path | None = None,
    max_cases: int = 20,
) -> str:
    if max_cases < 1:
        raise ValueError("max_cases must be at least 1")

    page_index = {page.id: page for page in pages}
    indexed = _index_rows(rows)
    deployments = _ordered_deployments(rows)
    all_repairs = _repair_pairs(indexed, deployments)
    regressions = _regression_pairs(indexed, deployments)
    cases = _select_representative_cases(indexed, deployments, max_cases=max_cases)

    lines = ["# Long-Graph v2 Preservation Casebook", ""]
    if source_paths or pages_path:
        lines.extend(["## Sources", ""])
        for path in source_paths or []:
            lines.append(f"- Results: `{path}`")
        if pages_path:
            lines.append(f"- Pages: `{pages_path}`")
        lines.append("")

    lines.extend(_scope_table(rows, pages, deployments, all_repairs, regressions, cases))
    lines.extend(_coverage_table(indexed, deployments, cases))
    lines.extend(_case_sections(cases, page_index))
    lines.extend(_interpretation(all_repairs, regressions, cases))
    return "\n".join(lines).rstrip() + "\n"


def _scope_table(
    rows: Sequence[Mapping[str, Any]],
    pages: Sequence[WebPage],
    deployments: Sequence[str],
    repairs: Sequence[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]],
    regressions: Sequence[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]],
    cases: Sequence[RepairCase],
) -> list[str]:
    direct_rows = [
        row
        for row in rows
        if str(row.get("condition")) in {*FIRST_CONDITIONS, SECOND_CONDITION}
        and row.get("expected_answer") in {"yes", "no"}
    ]
    return [
        "## Scope",
        "",
        "| Field | Value |",
        "| --- | ---: |",
        f"| Source rows read | {len(rows)} |",
        f"| A8/A9/A10 direct-control rows | {len(direct_rows)} |",
        f"| Page corpus rows | {len(pages)} |",
        f"| Deployments | {len(deployments)} |",
        f"| Repaired direct-control row pairs | {len(repairs)} |",
        f"| New A10 direct-control misses | {len(regressions)} |",
        f"| Representative repair cases | {len(cases)} |",
        "",
    ]


def _coverage_table(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, int], Mapping[str, Any]]]],
    deployments: Sequence[str],
    cases: Sequence[RepairCase],
) -> list[str]:
    lines = [
        "## Repair Coverage",
        "",
        "| Deployment | Comparison | Direct paired rows | Repairs | New A10 misses | Representative tasks |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    case_keys = {
        (case.deployment, case.first_condition, case.task_id)
        for case in cases
    }
    for deployment in deployments:
        deployment_index = indexed.get(deployment, {})
        for first_condition in FIRST_CONDITIONS:
            first_rows = deployment_index.get(first_condition, {})
            second_rows = deployment_index.get(SECOND_CONDITION, {})
            paired = _paired_direct_rows(first_rows, second_rows)
            repairs = [
                (first_row, second_row)
                for first_row, second_row in paired
                if not _is_correct(first_row) and _is_correct(second_row)
            ]
            regressions = [
                (first_row, second_row)
                for first_row, second_row in paired
                if _is_correct(first_row) and not _is_correct(second_row)
            ]
            representative_tasks = {
                task_id
                for dep, condition, task_id in case_keys
                if dep == deployment and condition == first_condition
            }
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(deployment),
                        _cell(f"{first_condition} -> {SECOND_CONDITION}"),
                        str(len(paired)),
                        str(len(repairs)),
                        str(len(regressions)),
                        str(len(representative_tasks)),
                    ]
                )
                + " |"
            )
    lines.append("")
    return lines


def _case_sections(cases: Sequence[RepairCase], page_index: Mapping[str, WebPage]) -> list[str]:
    lines = ["## Representative Cases", ""]
    if not cases:
        lines.extend(["No A8/A9 direct-control repair cases were found.", ""])
        return lines

    for index, case in enumerate(cases, start=1):
        first_correct = sum(1 for first_row, _second_row in case.paired_rows if _is_correct(first_row))
        second_correct = sum(1 for _first_row, second_row in case.paired_rows if _is_correct(second_row))
        first_answers = _answer_counts(first_row for first_row, _second_row in case.paired_rows)
        second_answers = _answer_counts(second_row for _first_row, second_row in case.paired_rows)
        first_labels = _row_relation_labels(case.first_row)
        second_labels = _row_relation_labels(case.second_row)
        label_changes = _label_changes(case.first_row, case.second_row)
        overrides = _classifier_overrides(case.second_row)

        lines.extend(
            [
                f"### Case {index}: {case.deployment} {case.first_condition} repair on {case.task_id}",
                "",
                f"- Question: {_text(case.question)}",
                f"- Expected answer: `{case.expected_answer}`",
                (
                    f"- Representative repeat: {case.repeat_index}; "
                    f"{case.first_condition} answered `{case.first_row.get('actual_answer')}`, "
                    f"A10 answered `{case.second_row.get('actual_answer')}`."
                ),
                (
                    f"- Task paired-repeat result: {case.first_condition} correct "
                    f"{first_correct}/{len(case.paired_rows)} ({first_answers}); "
                    f"A10 correct {second_correct}/{len(case.paired_rows)} ({second_answers})."
                ),
                f"- Safety metrics: {_metric_summary(case.second_row)}",
                f"- First labels: {first_labels}",
                f"- A10 labels: {second_labels}",
                f"- Label changes: {label_changes}",
                f"- A10 classifier overrides: {overrides}",
                "",
                "Trusted current evidence cited by A10:",
                "",
            ]
        )
        lines.extend(_evidence_lines(case, page_index))
        lines.extend(
            [
                "",
                f"A10 conclusion excerpt: {_truncate(_conclusion(case.second_row), 420)}",
                "",
                (
                    "Why it matters: the earlier gate converted direct trusted evidence "
                    "into a false abstention, while A10 preserved the direct "
                    f"{'support' if case.expected_answer == 'yes' else 'refutation'} relation without "
                    "citing poisoned pages."
                ),
                "",
            ]
        )
    return lines


def _evidence_lines(case: RepairCase, page_index: Mapping[str, WebPage]) -> list[str]:
    cited_page_ids = _id_list(case.second_row.get("cited_page_ids"))
    lines: list[str] = []
    for page_id in cited_page_ids:
        page = page_index.get(page_id)
        if page is None:
            lines.append(f"- `{page_id}`: missing from page corpus")
            continue
        support = page.supports_tasks.get(case.task_id, "not_listed")
        lines.append(
            "- "
            + f"`{page.id}`: {page.title} "
            + f"({page.trust_label}/{page.freshness}, supports task: `{support}`). "
            + _text(page.summary)
        )
    if not lines:
        lines.append("- No A10 citations recorded.")
    return lines


def _interpretation(
    repairs: Sequence[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]],
    regressions: Sequence[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]],
    cases: Sequence[RepairCase],
) -> list[str]:
    repaired_tasks = sorted({case.task_id for case in cases})
    return [
        "## Interpretation",
        "",
        (
            "The casebook makes the paired statistical appendix auditable at the "
            "row level. It surfaces representative direct-control rows where A8 "
            "or A9 abstained despite trusted current pages directly supporting "
            "or refuting the proposition, then shows the paired A10 row on the "
            "same deployment, task, and repeat."
        ),
        "",
        (
            f"Across the selected result files, there are {len(repairs)} repaired "
            f"direct-control row pairs and {len(regressions)} new A10 "
            "direct-control misses. The representative cases cover "
            f"{len(repaired_tasks)} unique tasks: {', '.join(repaired_tasks) if repaired_tasks else 'none'}."
        ),
        "",
    ]


def _select_representative_cases(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, int], Mapping[str, Any]]]],
    deployments: Sequence[str],
    max_cases: int,
) -> list[RepairCase]:
    cases: list[RepairCase] = []
    for deployment in deployments:
        deployment_index = indexed.get(deployment, {})
        for first_condition in FIRST_CONDITIONS:
            first_rows = deployment_index.get(first_condition, {})
            second_rows = deployment_index.get(SECOND_CONDITION, {})
            grouped: dict[str, list[tuple[Mapping[str, Any], Mapping[str, Any]]]] = defaultdict(list)
            repaired: dict[str, list[tuple[Mapping[str, Any], Mapping[str, Any]]]] = defaultdict(list)
            for first_row, second_row in _paired_direct_rows(first_rows, second_rows):
                task_id = str(first_row.get("task_id"))
                grouped[task_id].append((first_row, second_row))
                if not _is_correct(first_row) and _is_correct(second_row):
                    repaired[task_id].append((first_row, second_row))
            for task_id in sorted(repaired):
                paired_rows = sorted(
                    grouped[task_id],
                    key=lambda pair: int(pair[0].get("repeat_index", 1) or 1),
                )
                repair_rows = sorted(
                    repaired[task_id],
                    key=lambda pair: int(pair[0].get("repeat_index", 1) or 1),
                )
                first_row, second_row = repair_rows[0]
                cases.append(
                    RepairCase(
                        deployment=deployment,
                        first_condition=first_condition,
                        task_id=task_id,
                        repeat_index=int(first_row.get("repeat_index", 1) or 1),
                        expected_answer=str(first_row.get("expected_answer")),
                        question=str(first_row.get("question") or second_row.get("question") or ""),
                        first_row=first_row,
                        second_row=second_row,
                        paired_rows=tuple(paired_rows),
                    )
                )
                if len(cases) >= max_cases:
                    return cases
    return cases


def _repair_pairs(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, int], Mapping[str, Any]]]],
    deployments: Sequence[str],
) -> list[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]]:
    pairs: list[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]] = []
    for deployment in deployments:
        deployment_index = indexed.get(deployment, {})
        for first_condition in FIRST_CONDITIONS:
            for first_row, second_row in _paired_direct_rows(
                deployment_index.get(first_condition, {}),
                deployment_index.get(SECOND_CONDITION, {}),
            ):
                if not _is_correct(first_row) and _is_correct(second_row):
                    pairs.append((deployment, first_condition, first_row, second_row))
    return pairs


def _regression_pairs(
    indexed: Mapping[str, Mapping[str, Mapping[tuple[str, int], Mapping[str, Any]]]],
    deployments: Sequence[str],
) -> list[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]]:
    pairs: list[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]] = []
    for deployment in deployments:
        deployment_index = indexed.get(deployment, {})
        for first_condition in FIRST_CONDITIONS:
            for first_row, second_row in _paired_direct_rows(
                deployment_index.get(first_condition, {}),
                deployment_index.get(SECOND_CONDITION, {}),
            ):
                if _is_correct(first_row) and not _is_correct(second_row):
                    pairs.append((deployment, first_condition, first_row, second_row))
    return pairs


def _paired_direct_rows(
    first_rows: Mapping[tuple[str, int], Mapping[str, Any]],
    second_rows: Mapping[tuple[str, int], Mapping[str, Any]],
) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    paired: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
    for key in sorted(set(first_rows) & set(second_rows)):
        first_row = first_rows[key]
        second_row = second_rows[key]
        first_expected = first_row.get("expected_answer")
        second_expected = second_row.get("expected_answer")
        if first_expected == second_expected and first_expected in {"yes", "no"}:
            paired.append((first_row, second_row))
    return paired


def _index_rows(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, dict[tuple[str, int], Mapping[str, Any]]]]:
    indexed: dict[str, dict[str, dict[tuple[str, int], Mapping[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in rows:
        condition = str(row.get("condition"))
        if condition not in {*FIRST_CONDITIONS, SECOND_CONDITION}:
            continue
        indexed[_deployment_label(row)][condition][_pair_key(row)] = row
    return {
        deployment: {condition: dict(condition_rows) for condition, condition_rows in condition_index.items()}
        for deployment, condition_index in indexed.items()
    }


def _pair_key(row: Mapping[str, Any]) -> tuple[str, int]:
    return (str(row.get("task_id")), int(row.get("repeat_index", 1) or 1))


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
        condition = str(row.get("condition"))
        if condition not in {*FIRST_CONDITIONS, SECOND_CONDITION}:
            continue
        deployment = _deployment_label(row)
        if deployment not in deployments:
            deployments.append(deployment)
    return deployments


def _row_relation_labels(row: Mapping[str, Any]) -> str:
    labels = _row_relation_label_map(row)
    if not labels:
        return "none"
    return "; ".join(f"{page_id}:{labels[page_id]}" for page_id in sorted(labels))


def _row_relation_label_map(row: Mapping[str, Any]) -> dict[str, str]:
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

    result: dict[str, str] = {}
    for entry in _relation_classifier_entries(row):
        if entry.page_id:
            result[entry.page_id] = entry.final_label
    return result


@dataclass(frozen=True)
class RelationEntry:
    page_id: str
    raw_label: str
    final_label: str
    override: bool


def _relation_classifier_entries(row: Mapping[str, Any]) -> list[RelationEntry]:
    metadata = row.get("provider_metadata")
    if not isinstance(metadata, Mapping):
        return []
    entries = metadata.get("relation_classifier")
    if not isinstance(entries, RuntimeSequence) or isinstance(entries, (str, bytes)):
        return []

    normalized: list[RelationEntry] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        final_label = str(entry.get("evidence_relation") or "unknown")
        raw_label = str(entry.get("raw_evidence_relation") or final_label)
        normalized.append(
            RelationEntry(
                page_id=str(entry.get("page_id") or "unknown_page"),
                raw_label=raw_label,
                final_label=final_label,
                override=bool(entry.get("calibration_override")) or raw_label != final_label,
            )
        )
    return normalized


def _classifier_overrides(row: Mapping[str, Any]) -> str:
    overrides = [entry for entry in _relation_classifier_entries(row) if entry.override]
    if not overrides:
        return "none"
    return "; ".join(
        f"{entry.page_id}:{entry.raw_label} -> {entry.final_label}" for entry in overrides
    )


def _label_changes(first_row: Mapping[str, Any], second_row: Mapping[str, Any]) -> str:
    first_labels = _row_relation_label_map(first_row)
    second_labels = _row_relation_label_map(second_row)
    changes: list[str] = []
    for page_id in sorted(set(first_labels) | set(second_labels)):
        first_label = first_labels.get(page_id, "missing")
        second_label = second_labels.get(page_id, "missing")
        if first_label != second_label:
            changes.append(f"{page_id}:{first_label} -> {second_label}")
    return "; ".join(changes) if changes else "none"


def _answer_counts(rows: Iterable[Mapping[str, Any]]) -> str:
    counter: Counter[str] = Counter(str(row.get("actual_answer")) for row in rows)
    order = ["yes", "no", "insufficient_evidence"]
    labels = [label for label in order if counter.get(label)]
    labels.extend(sorted(label for label in counter if label not in labels))
    return "; ".join(f"{label}={counter[label]}" for label in labels) if labels else "none"


def _metric_summary(row: Mapping[str, Any]) -> str:
    return "; ".join(
        f"{name}={_metric(row, name)}"
        for name in [
            "attack_success",
            "cited_poisoned",
            "filtered_poisoned",
            "provider_error",
        ]
    )


def _metric(row: Mapping[str, Any], name: str) -> Any:
    metrics = row.get("metrics")
    if isinstance(metrics, Mapping):
        return metrics.get(name)
    return None


def _is_correct(row: Mapping[str, Any]) -> bool:
    return bool(_metric(row, "answer_accuracy"))


def _conclusion(row: Mapping[str, Any]) -> str:
    answer = row.get("answer")
    if isinstance(answer, Mapping):
        return str(answer.get("conclusion") or "")
    return ""


def _id_list(value: Any) -> list[str]:
    if isinstance(value, RuntimeSequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return []


def _truncate(value: str, limit: int) -> str:
    text = _text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _text(value: str) -> str:
    return " ".join(str(value).split())


def _cell(value: str) -> str:
    return _text(str(value)).replace("|", "\\|")
