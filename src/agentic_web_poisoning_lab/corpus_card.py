from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence

from agentic_web_poisoning_lab.io import load_pages, load_tasks, write_text
from agentic_web_poisoning_lab.schema import TaskCase, WebPage


def write_corpus_card(tasks_path: Path, pages_path: Path, out_path: Path) -> str:
    markdown = build_corpus_card(load_tasks(tasks_path), load_pages(pages_path), tasks_path, pages_path)
    write_text(out_path, markdown)
    return markdown


def build_corpus_card(
    tasks: Sequence[TaskCase],
    pages: Sequence[WebPage],
    tasks_path: Path | None = None,
    pages_path: Path | None = None,
) -> str:
    page_index = {page.id: page for page in pages}
    lines = ["# Long-Graph v2 Corpus Card", ""]
    if tasks_path or pages_path:
        lines.extend(["## Sources", ""])
        if tasks_path:
            lines.append(f"- Tasks: `{tasks_path}`")
        if pages_path:
            lines.append(f"- Pages: `{pages_path}`")
        lines.append("")

    lines.extend(_scope(tasks, pages))
    lines.extend(_task_distribution(tasks))
    lines.extend(_page_distribution(pages))
    lines.extend(_domain_distribution(tasks, pages))
    lines.extend(_task_structure(tasks, page_index))
    lines.extend(_interpretation(tasks, pages))
    return "\n".join(lines).rstrip() + "\n"


def _scope(tasks: Sequence[TaskCase], pages: Sequence[WebPage]) -> list[str]:
    required_counts = Counter(len(task.required_page_ids) for task in tasks)
    attack_counts = Counter(len(task.attack_page_ids) for task in tasks)
    domains = {_task_domain(task) for task in tasks}
    return [
        "## Scope",
        "",
        "| Field | Value |",
        "| --- | ---: |",
        f"| Tasks | {len(tasks)} |",
        f"| Pages | {len(pages)} |",
        f"| Domains | {len(domains)} |",
        f"| Required pages per task | {_format_counter(required_counts)} |",
        f"| Attack pages per task | {_format_counter(attack_counts)} |",
        "",
    ]


def _task_distribution(tasks: Sequence[TaskCase]) -> list[str]:
    return [
        "## Task Distribution",
        "",
        "| Field | Distribution |",
        "| --- | --- |",
        f"| Expected answers | {_format_counter(Counter(task.expected_answer for task in tasks))} |",
        f"| Attack types | {_format_counter(Counter(str(task.attack_type) for task in tasks))} |",
        (
            f"| Attack target answers | "
            f"{_format_counter(Counter(str(task.attack_target_answer) for task in tasks))} |"
        ),
        "",
    ]


def _page_distribution(pages: Sequence[WebPage]) -> list[str]:
    supported_answers = Counter(
        support for page in pages for support in page.supports_tasks.values()
    )
    attack_types = Counter(str(page.attack_type) if page.attack_type else "none" for page in pages)
    return [
        "## Page Distribution",
        "",
        "| Field | Distribution |",
        "| --- | --- |",
        f"| Poisoned pages | {_format_counter(Counter(str(page.is_poisoned) for page in pages))} |",
        f"| Trust labels | {_format_counter(Counter(page.trust_label for page in pages))} |",
        f"| Freshness labels | {_format_counter(Counter(page.freshness for page in pages))} |",
        f"| Attack types | {_format_counter(attack_types)} |",
        f"| Task support labels | {_format_counter(supported_answers)} |",
        "",
    ]


def _domain_distribution(tasks: Sequence[TaskCase], pages: Sequence[WebPage]) -> list[str]:
    task_domains: dict[str, list[TaskCase]] = defaultdict(list)
    for task in tasks:
        task_domains[_task_domain(task)].append(task)
    page_domains: dict[str, list[WebPage]] = defaultdict(list)
    for page in pages:
        page_domains[_page_domain(page.id)].append(page)

    lines = [
        "## Domain Distribution",
        "",
        "| Domain | Tasks | Pages | Expected answers | Poisoned pages |",
        "| --- | ---: | ---: | --- | ---: |",
    ]
    for domain in sorted(set(task_domains) | set(page_domains)):
        domain_tasks = task_domains.get(domain, [])
        domain_pages = page_domains.get(domain, [])
        expected = Counter(task.expected_answer for task in domain_tasks)
        poisoned = sum(1 for page in domain_pages if page.is_poisoned)
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(domain),
                    str(len(domain_tasks)),
                    str(len(domain_pages)),
                    _format_counter(expected),
                    str(poisoned),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _task_structure(tasks: Sequence[TaskCase], page_index: dict[str, WebPage]) -> list[str]:
    lines = [
        "## Per-Task Structure",
        "",
        "| Task | Domain | Expected | Attack type | Required pages | Attack pages | Attack target |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for task in sorted(tasks, key=lambda item: item.id):
        required_missing = [page_id for page_id in task.required_page_ids if page_id not in page_index]
        attack_missing = [page_id for page_id in task.attack_page_ids if page_id not in page_index]
        required_count = str(len(task.required_page_ids))
        attack_count = str(len(task.attack_page_ids))
        if required_missing:
            required_count += f" ({len(required_missing)} missing)"
        if attack_missing:
            attack_count += f" ({len(attack_missing)} missing)"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_cell(task.id)}`",
                    _cell(_task_domain(task)),
                    _cell(task.expected_answer),
                    _cell(str(task.attack_type)),
                    required_count,
                    attack_count,
                    _cell(str(task.attack_target_answer)),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _interpretation(tasks: Sequence[TaskCase], pages: Sequence[WebPage]) -> list[str]:
    expected = Counter(task.expected_answer for task in tasks)
    domains = {_task_domain(task) for task in tasks}
    poisoned = sum(1 for page in pages if page.is_poisoned)
    return [
        "## Interpretation",
        "",
        (
            "The long-graph v2 corpus is balanced across answer labels "
            f"({_format_counter(expected)}) and spans {len(domains)} campus AI "
            "governance domains. Every task has the same page budget, which keeps "
            "the hosted preservation comparisons focused on evidence handling "
            "rather than retrieval-depth differences."
        ),
        "",
        (
            f"The page set contains {poisoned}/{len(pages)} poisoned or adversarial "
            "distractor pages. This keeps attack pressure present while preserving "
            "a clean trusted/current evidence path for direct-support, direct-"
            "refutation, and insufficient-evidence controls."
        ),
        "",
    ]


def _task_domain(task: TaskCase) -> str:
    if task.required_page_ids:
        return _page_domain(task.required_page_ids[0])
    return "unknown"


def _page_domain(page_id: str) -> str:
    parts = page_id.split("_")
    if len(parts) >= 4 and parts[0] == "page" and parts[1] == "v2":
        return parts[2]
    return "unknown"


def _format_counter(counter: Counter[object]) -> str:
    if not counter:
        return "none"
    return "; ".join(f"{key}={counter[key]}" for key in sorted(counter, key=str))


def _cell(value: str) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")
