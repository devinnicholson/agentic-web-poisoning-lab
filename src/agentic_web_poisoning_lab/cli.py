from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic_web_poisoning_lab.agent import DeterministicWebAgent
from agentic_web_poisoning_lab.artifact_manifest import write_artifact_manifest
from agentic_web_poisoning_lab.artifact_validation import write_public_artifact_validation
from agentic_web_poisoning_lab.audit import write_audit_queue
from agentic_web_poisoning_lab.blind_audit import write_blind_audit_queue
from agentic_web_poisoning_lab.comparison import write_comparison_report
from agentic_web_poisoning_lab.conditions import CONDITIONS, DEFAULT_CONDITIONS
from agentic_web_poisoning_lab.corpus_card import write_corpus_card
from agentic_web_poisoning_lab.hosted import (
    DEFAULT_HOSTED_CONDITIONS,
    DEFAULT_HOSTED_TASK_IDS,
    AzureOpenAIChatClient,
    HostedConfigError,
    HostedWebAgent,
    azure_config_from_env,
)
from agentic_web_poisoning_lab.io import append_jsonl, load_pages, load_tasks, read_jsonl, write_jsonl
from agentic_web_poisoning_lab.metrics import summarize
from agentic_web_poisoning_lab.paired_analysis import write_paired_analysis, write_preservation_analysis
from agentic_web_poisoning_lab.preservation_casebook import write_preservation_casebook
from agentic_web_poisoning_lab.preservation_transitions import (
    write_preservation_transition_analysis,
)
from agentic_web_poisoning_lab.public_snapshot import (
    snapshot_is_public_safe,
    write_public_snapshot,
)
from agentic_web_poisoning_lab.research_stats import write_research_stats
from agentic_web_poisoning_lab.reporting import write_markdown_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agentic-web-poisoning-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run deterministic local benchmark.")
    run_parser.add_argument("--tasks", type=Path, default=Path("data/tasks.seed.jsonl"))
    run_parser.add_argument("--pages", type=Path, default=Path("data/pages.seed.jsonl"))
    run_parser.add_argument(
        "--conditions",
        default=",".join(DEFAULT_CONDITIONS),
        help="Comma-separated condition IDs.",
    )
    run_parser.add_argument("--out-dir", type=Path, default=Path("experiments/results/local"))

    hosted_parser = subparsers.add_parser("run-hosted", help="Run Azure OpenAI smoke validation.")
    hosted_parser.add_argument("--tasks", type=Path, default=Path("data/tasks.seed.jsonl"))
    hosted_parser.add_argument("--pages", type=Path, default=Path("data/pages.seed.jsonl"))
    hosted_parser.add_argument(
        "--conditions",
        default=",".join(DEFAULT_HOSTED_CONDITIONS),
        help="Comma-separated condition IDs.",
    )
    hosted_parser.add_argument(
        "--task-ids",
        default=",".join(DEFAULT_HOSTED_TASK_IDS),
        help="Comma-separated task IDs for the hosted run, or 'all'.",
    )
    hosted_parser.add_argument("--max-cases", type=int, default=None)
    hosted_parser.add_argument("--env-file", type=Path, default=Path(".env"))
    hosted_parser.add_argument("--out-dir", type=Path, default=Path("experiments/results/hosted-smoke"))
    hosted_parser.add_argument("--delay-seconds", type=float, default=0.0)
    hosted_parser.add_argument("--run-mode", default="hosted_smoke")
    hosted_parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="Repeat every planned task/condition pair this many times.",
    )
    hosted_parser.add_argument(
        "--resume",
        action="store_true",
        help="Append missing hosted rows and skip existing task/condition pairs.",
    )

    report_parser = subparsers.add_parser("report", help="Generate Markdown report.")
    report_parser.add_argument(
        "--results",
        type=Path,
        default=Path("experiments/results/local/results.jsonl"),
    )
    report_parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/results/local/report.md"),
    )

    compare_parser = subparsers.add_parser("compare", help="Compare hosted rows against local rows.")
    compare_parser.add_argument(
        "--local",
        type=Path,
        default=Path("experiments/results/local/results.jsonl"),
    )
    compare_parser.add_argument(
        "--hosted",
        type=Path,
        default=Path("experiments/results/hosted-focused/results.jsonl"),
    )
    compare_parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/results/hosted-focused/comparison.md"),
    )

    stats_parser = subparsers.add_parser("stats", help="Generate research statistics report.")
    stats_parser.add_argument(
        "--results",
        type=Path,
        default=Path("experiments/results/hosted-full/results.jsonl"),
    )
    stats_parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/results/hosted-full/stats.md"),
    )

    paired_parser = subparsers.add_parser(
        "paired-analysis",
        help="Generate a paired condition-analysis appendix from one or more result files.",
    )
    paired_parser.add_argument(
        "--results",
        type=Path,
        nargs="+",
        required=True,
        help="One or more result JSONL files to merge before pairing rows.",
    )
    paired_parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/paired-condition-analysis.md"),
    )

    preservation_parser = subparsers.add_parser(
        "preservation-analysis",
        help="Generate a paired A8/A9/A10 preservation-analysis appendix.",
    )
    preservation_parser.add_argument(
        "--results",
        type=Path,
        nargs="+",
        required=True,
        help="One or more result JSONL files to merge before pairing rows by deployment.",
    )
    preservation_parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/paired-preservation-analysis.md"),
    )

    casebook_parser = subparsers.add_parser(
        "preservation-casebook",
        help="Generate a qualitative A8/A9/A10 preservation repair casebook.",
    )
    casebook_parser.add_argument(
        "--results",
        type=Path,
        nargs="+",
        required=True,
        help="One or more result JSONL files to merge before pairing rows by deployment.",
    )
    casebook_parser.add_argument(
        "--pages",
        type=Path,
        default=Path("data/pages.graph-long-v2.jsonl"),
    )
    casebook_parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/long-graph-v2-preservation-casebook.md"),
    )
    casebook_parser.add_argument(
        "--max-cases",
        type=int,
        default=20,
        help="Maximum representative repaired rows to include.",
    )

    transition_parser = subparsers.add_parser(
        "preservation-transitions",
        help="Generate a page-label transition analysis for A8/A9/A10 preservation repairs.",
    )
    transition_parser.add_argument(
        "--results",
        type=Path,
        nargs="+",
        required=True,
        help="One or more result JSONL files to merge before pairing rows by deployment.",
    )
    transition_parser.add_argument(
        "--pages",
        type=Path,
        default=Path("data/pages.graph-long-v2.jsonl"),
    )
    transition_parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/long-graph-v2-preservation-transition-analysis.md"),
    )

    manifest_parser = subparsers.add_parser(
        "artifact-manifest",
        help="Generate a deterministic research artifact checksum manifest.",
    )
    manifest_parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/research-artifact-manifest.md"),
    )

    artifact_validation_parser = subparsers.add_parser(
        "artifact-validation",
        help="Validate committed public long-graph v2 artifacts.",
    )
    artifact_validation_parser.add_argument(
        "--tasks",
        type=Path,
        default=Path("data/tasks.graph-long-v2.jsonl"),
    )
    artifact_validation_parser.add_argument(
        "--pages",
        type=Path,
        default=Path("data/pages.graph-long-v2.jsonl"),
    )
    artifact_validation_parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/long-graph-v2-public-artifact-validation.md"),
    )

    corpus_card_parser = subparsers.add_parser(
        "corpus-card",
        help="Generate a deterministic corpus card for a task/page dataset.",
    )
    corpus_card_parser.add_argument(
        "--tasks",
        type=Path,
        default=Path("data/tasks.graph-long-v2.jsonl"),
    )
    corpus_card_parser.add_argument(
        "--pages",
        type=Path,
        default=Path("data/pages.graph-long-v2.jsonl"),
    )
    corpus_card_parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/long-graph-v2-corpus-card.md"),
    )

    public_snapshot_parser = subparsers.add_parser(
        "public-snapshot",
        help="Write a sanitized public snapshot from hosted result rows.",
    )
    public_snapshot_parser.add_argument(
        "--results",
        type=Path,
        required=True,
        help="Private or local result JSONL file to sanitize.",
    )
    public_snapshot_parser.add_argument(
        "--out-results",
        type=Path,
        required=True,
        help="Public JSONL snapshot path.",
    )
    public_snapshot_parser.add_argument(
        "--out-summary",
        type=Path,
        required=True,
        help="Public summary JSON path regenerated from the sanitized rows.",
    )

    audit_parser = subparsers.add_parser("audit", help="Generate a human audit queue.")
    audit_parser.add_argument(
        "--results",
        type=Path,
        default=Path("experiments/results/local/results.jsonl"),
    )
    audit_parser.add_argument("--pages", type=Path, default=Path("data/pages.seed.jsonl"))
    audit_parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/results/local/audit-queue.md"),
    )
    audit_parser.add_argument("--max-rows", type=int, default=80)

    blind_audit_parser = subparsers.add_parser(
        "blind-audit",
        help="Generate a blinded JSONL reviewer queue and optional unblinding key.",
    )
    blind_audit_parser.add_argument(
        "--results",
        type=Path,
        nargs="+",
        required=True,
        help="One or more public result JSONL files.",
    )
    blind_audit_parser.add_argument(
        "--pages",
        type=Path,
        default=Path("data/pages.graph-long-v2.jsonl"),
    )
    blind_audit_parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/long-graph-v2/blind-audit-queue.jsonl"),
    )
    blind_audit_parser.add_argument(
        "--out-key",
        type=Path,
        default=None,
        help="Optional unblinding key with task, condition, answer, and metric fields.",
    )
    blind_audit_parser.add_argument("--max-items", type=int, default=96)

    args = parser.parse_args(argv)
    if args.command == "run":
        return run_command(args)
    if args.command == "run-hosted":
        return run_hosted_command(args)
    if args.command == "report":
        return report_command(args)
    if args.command == "compare":
        return compare_command(args)
    if args.command == "stats":
        return stats_command(args)
    if args.command == "paired-analysis":
        return paired_analysis_command(args)
    if args.command == "preservation-analysis":
        return preservation_analysis_command(args)
    if args.command == "preservation-casebook":
        return preservation_casebook_command(args)
    if args.command == "preservation-transitions":
        return preservation_transitions_command(args)
    if args.command == "artifact-manifest":
        return artifact_manifest_command(args)
    if args.command == "artifact-validation":
        return artifact_validation_command(args)
    if args.command == "corpus-card":
        return corpus_card_command(args)
    if args.command == "public-snapshot":
        return public_snapshot_command(args)
    if args.command == "audit":
        return audit_command(args)
    if args.command == "blind-audit":
        return blind_audit_command(args)
    raise AssertionError(f"Unhandled command: {args.command}")


def run_command(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.tasks)
    pages = load_pages(args.pages)
    condition_ids = parse_conditions(args.conditions)
    results = DeterministicWebAgent(pages).run(tasks, condition_ids)
    rows = [result.to_dict() for result in results]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "results.jsonl", rows)
    summary = summarize(read_jsonl(args.out_dir / "results.jsonl"))
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    print(f"Wrote {len(rows)} result rows to {args.out_dir / 'results.jsonl'}")
    print(f"Wrote summary to {args.out_dir / 'summary.json'}")
    print_summary(summary)
    return 0


def run_hosted_command(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.tasks)
    pages = load_pages(args.pages)
    condition_ids = parse_conditions(args.conditions)
    task_ids = parse_task_ids(args.task_ids, tasks)
    if args.repeats < 1:
        raise SystemExit("--repeats must be at least 1")
    try:
        config = azure_config_from_env(args.env_file)
    except HostedConfigError as exc:
        raise SystemExit(str(exc)) from exc

    client = AzureOpenAIChatClient(config)
    agent = HostedWebAgent(
        pages,
        client,
        provider_metadata=config.public_metadata(),
        delay_seconds=args.delay_seconds,
        run_mode=args.run_mode,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    results_path = args.out_dir / "results.jsonl"
    existing_rows = read_jsonl(results_path) if args.resume and results_path.exists() else []
    skip_keys = completed_keys(existing_rows)
    run_id = resume_run_id(existing_rows)
    if args.resume and existing_rows:
        print(f"Resuming hosted run with {len(skip_keys)} completed rows from {results_path}", flush=True)
    else:
        write_jsonl(results_path, [])

    planned_total = planned_hosted_total(task_ids, condition_ids, args.max_cases, args.repeats)
    rows = list(existing_rows)
    for row in agent.iter_run(
        tasks,
        condition_ids,
        task_ids,
        max_cases=args.max_cases,
        run_id=run_id,
        skip_keys=skip_keys,
        repeat_count=args.repeats,
    ):
        append_jsonl(results_path, row)
        rows.append(row)
        skip_keys.add(completed_key(row))
        print(hosted_progress_line(row, len(skip_keys), planned_total), flush=True)

    summary = summarize(read_jsonl(results_path))
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    print(f"Wrote {len(rows)} hosted result rows to {results_path}")
    print(f"Wrote hosted summary to {args.out_dir / 'summary.json'}")
    print_summary(summary)
    return 0


def report_command(args: argparse.Namespace) -> int:
    markdown = write_markdown_report(args.results, args.out)
    print(f"Wrote Markdown report to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def compare_command(args: argparse.Namespace) -> int:
    markdown = write_comparison_report(args.local, args.hosted, args.out)
    print(f"Wrote comparison report to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def stats_command(args: argparse.Namespace) -> int:
    markdown = write_research_stats(args.results, args.out)
    print(f"Wrote research statistics to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def paired_analysis_command(args: argparse.Namespace) -> int:
    markdown = write_paired_analysis(args.results, args.out)
    print(f"Wrote paired analysis to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def preservation_analysis_command(args: argparse.Namespace) -> int:
    markdown = write_preservation_analysis(args.results, args.out)
    print(f"Wrote preservation analysis to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def preservation_casebook_command(args: argparse.Namespace) -> int:
    markdown = write_preservation_casebook(
        args.results,
        args.pages,
        args.out,
        max_cases=args.max_cases,
    )
    print(f"Wrote preservation casebook to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def preservation_transitions_command(args: argparse.Namespace) -> int:
    markdown = write_preservation_transition_analysis(
        args.results,
        args.pages,
        args.out,
    )
    print(f"Wrote preservation transitions to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def artifact_manifest_command(args: argparse.Namespace) -> int:
    markdown = write_artifact_manifest(args.out)
    print(f"Wrote artifact manifest to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def artifact_validation_command(args: argparse.Namespace) -> int:
    markdown = write_public_artifact_validation(args.tasks, args.pages, args.out)
    print(f"Wrote artifact validation report to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def corpus_card_command(args: argparse.Namespace) -> int:
    markdown = write_corpus_card(args.tasks, args.pages, args.out)
    print(f"Wrote corpus card to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def public_snapshot_command(args: argparse.Namespace) -> int:
    rows, summary = write_public_snapshot(args.results, args.out_results, args.out_summary)
    if not snapshot_is_public_safe(rows):
        raise SystemExit("public snapshot contains unredacted provider identifiers")

    print(f"Wrote {len(rows)} public rows to {args.out_results}")
    print(f"Wrote public summary to {args.out_summary}")
    print_summary(summary)
    return 0


def audit_command(args: argparse.Namespace) -> int:
    markdown = write_audit_queue(args.results, args.pages, args.out, max_rows=args.max_rows)
    print(f"Wrote human audit queue to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def blind_audit_command(args: argparse.Namespace) -> int:
    queue, key = write_blind_audit_queue(
        args.results,
        args.pages,
        args.out,
        out_key_path=args.out_key,
        max_items=args.max_items,
    )
    print(f"Wrote {len(queue)} blinded audit items to {args.out}")
    if args.out_key is not None:
        print(f"Wrote {len(key)} unblinding key rows to {args.out_key}")
    return 0


def parse_conditions(value: str) -> list[str]:
    condition_ids = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [condition_id for condition_id in condition_ids if condition_id not in CONDITIONS]
    if unknown:
        raise SystemExit(f"Unknown condition(s): {', '.join(unknown)}")
    return condition_ids


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_task_ids(value: str, tasks: list[object]) -> list[str]:
    if value.strip().lower() == "all":
        return [str(getattr(task, "id")) for task in tasks]
    return parse_csv(value)


def completed_keys(rows: list[dict[str, object]]) -> set[tuple[str, str, int]]:
    return {
        completed_key(row)
        for row in rows
        if row.get("task_id") and row.get("condition")
    }


def completed_key(row: dict[str, object]) -> tuple[str, str, int]:
    repeat_index = row.get("repeat_index")
    if not isinstance(repeat_index, int):
        repeat_index = 1
    return (str(row.get("task_id")), str(row.get("condition")), repeat_index)


def resume_run_id(rows: list[dict[str, object]]) -> str | None:
    run_ids = [str(row.get("run_id")) for row in rows if row.get("run_id")]
    return run_ids[0] if run_ids else None


def planned_hosted_total(
    task_ids: list[str],
    condition_ids: list[str],
    max_cases: int | None,
    repeat_count: int = 1,
) -> int:
    task_count = min(len(task_ids), max_cases) if max_cases is not None else len(task_ids)
    return task_count * len(condition_ids) * repeat_count


def hosted_progress_line(row: dict[str, object], completed: int, total: int) -> str:
    metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
    metadata = row.get("provider_metadata") if isinstance(row.get("provider_metadata"), dict) else {}
    retries = metadata.get("retry_count", "n/a")
    return (
        f"[{completed}/{total}] "
        f"{row.get('condition')} {row.get('task_id')} "
        f"repeat={row.get('repeat_index', 1)} "
        f"answer={row.get('actual_answer')} "
        f"attack_success={metrics.get('attack_success')} "
        f"provider_error={metrics.get('provider_error')} "
        f"retries={retries}"
    )


def print_summary(summary: list[dict[str, object]]) -> None:
    columns = [
        "condition",
        "total_cases",
        "attack_cases",
        "answer_accuracy",
        "attack_success_rate",
        "cited_poisoned_rate",
        "filtered_poisoned_rate",
        "provider_block_rate",
        "provider_error_rate",
    ]
    widths = {
        column: max(len(column), *(len(_summary_value(row.get(column))) for row in summary))
        for column in columns
    }
    print(" | ".join(column.ljust(widths[column]) for column in columns))
    print("-+-".join("-" * widths[column] for column in columns))
    for row in summary:
        print(" | ".join(_summary_value(row.get(column)).ljust(widths[column]) for column in columns))


def _summary_value(value: object) -> str:
    if value is None:
        return "n/a"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
