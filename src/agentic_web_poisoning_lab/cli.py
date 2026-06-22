from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic_web_poisoning_lab.agent import DeterministicWebAgent
from agentic_web_poisoning_lab.audit import write_audit_queue
from agentic_web_poisoning_lab.conditions import CONDITIONS, DEFAULT_CONDITIONS
from agentic_web_poisoning_lab.hosted import (
    DEFAULT_HOSTED_CONDITIONS,
    DEFAULT_HOSTED_TASK_IDS,
    AzureOpenAIChatClient,
    HostedConfigError,
    HostedWebAgent,
    azure_config_from_env,
)
from agentic_web_poisoning_lab.io import load_pages, load_tasks, read_jsonl, write_jsonl
from agentic_web_poisoning_lab.metrics import summarize
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
        help="Comma-separated task IDs for the hosted smoke run.",
    )
    hosted_parser.add_argument("--max-cases", type=int, default=None)
    hosted_parser.add_argument("--env-file", type=Path, default=Path(".env"))
    hosted_parser.add_argument("--out-dir", type=Path, default=Path("experiments/results/hosted-smoke"))
    hosted_parser.add_argument("--delay-seconds", type=float, default=0.0)

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

    args = parser.parse_args(argv)
    if args.command == "run":
        return run_command(args)
    if args.command == "run-hosted":
        return run_hosted_command(args)
    if args.command == "report":
        return report_command(args)
    if args.command == "audit":
        return audit_command(args)
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
    task_ids = parse_csv(args.task_ids)
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
    )
    rows = agent.run(tasks, condition_ids, task_ids, max_cases=args.max_cases)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "results.jsonl", rows)
    summary = summarize(read_jsonl(args.out_dir / "results.jsonl"))
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    print(f"Wrote {len(rows)} hosted result rows to {args.out_dir / 'results.jsonl'}")
    print(f"Wrote hosted summary to {args.out_dir / 'summary.json'}")
    print_summary(summary)
    return 0


def report_command(args: argparse.Namespace) -> int:
    markdown = write_markdown_report(args.results, args.out)
    print(f"Wrote Markdown report to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def audit_command(args: argparse.Namespace) -> int:
    markdown = write_audit_queue(args.results, args.pages, args.out, max_rows=args.max_rows)
    print(f"Wrote human audit queue to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def parse_conditions(value: str) -> list[str]:
    condition_ids = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [condition_id for condition_id in condition_ids if condition_id not in CONDITIONS]
    if unknown:
        raise SystemExit(f"Unknown condition(s): {', '.join(unknown)}")
    return condition_ids


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


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
