from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic_web_poisoning_lab.agent import DeterministicWebAgent
from agentic_web_poisoning_lab.conditions import CONDITIONS, DEFAULT_CONDITIONS
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

    args = parser.parse_args(argv)
    if args.command == "run":
        return run_command(args)
    if args.command == "report":
        return report_command(args)
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


def report_command(args: argparse.Namespace) -> int:
    markdown = write_markdown_report(args.results, args.out)
    print(f"Wrote Markdown report to {args.out} ({len(markdown.splitlines())} lines)")
    return 0


def parse_conditions(value: str) -> list[str]:
    condition_ids = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [condition_id for condition_id in condition_ids if condition_id not in CONDITIONS]
    if unknown:
        raise SystemExit(f"Unknown condition(s): {', '.join(unknown)}")
    return condition_ids


def print_summary(summary: list[dict[str, object]]) -> None:
    columns = [
        "condition",
        "total_cases",
        "attack_cases",
        "answer_accuracy",
        "attack_success_rate",
        "cited_poisoned_rate",
        "filtered_poisoned_rate",
    ]
    widths = {
        column: max(len(column), *(len(str(row.get(column, ""))) for row in summary))
        for column in columns
    }
    print(" | ".join(column.ljust(widths[column]) for column in columns))
    print("-+-".join("-" * widths[column] for column in columns))
    for row in summary:
        print(" | ".join(str(row.get(column, "")).ljust(widths[column]) for column in columns))


if __name__ == "__main__":
    raise SystemExit(main())
