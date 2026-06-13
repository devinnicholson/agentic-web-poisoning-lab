# Project Plan

## Goal

Create a credible, low-cost research artifact showing how web-browsing agents
fail or recover when pages contain adversarial or misleading content.

## Research Outputs

- Synthetic web-page dataset with page trust, freshness, and attack labels.
- Local deterministic harness for repeatable failures.
- Hosted Azure validation with a real model once local behavior is stable.
- Human audit queue for source selection, citation support, abstention quality,
  and action safety.
- Static demo showing a single task across A1, A3, and A4.

## Milestones

| Milestone | Output | Success Criterion |
| --- | --- | --- |
| M0 scaffold | Repo, protocol, seed data | Project can be reviewed without extra context. |
| M1 local harness | CLI runs seed cases under A0-A4 | Deterministic report shows at least one baseline failure. |
| M2 dataset expansion | 30-50 synthetic tasks | Attack classes and benign controls are balanced. |
| M3 audit workflow | Markdown audit queue | Provider blocks, bad citations, and unsafe actions are reviewable. |
| M4 hosted validation | Azure-backed run | Hosted result is summarized without raw generated outputs in Git. |
| M5 demo artifact | Static HTML trace | Five-minute demo works without credentials. |

## Engineering Approach

- Keep page parsing structured. Store page metadata, body summary, trust label,
  freshness, and attack class separately.
- Treat a provider block or refusal as an outcome, not a crash.
- Separate answer correctness from source quality and action safety.
- Redact raw attack text in public docs and demos.
- Reuse the RAG lab's discipline: generated outputs stay under
  `experiments/results/` and out of Git.

## First Implementation Slice

1. Define schema objects for task cases, web pages, agent traces, and metrics.
2. Implement a deterministic local browsing agent.
3. Add source-ranking and filtering conditions.
4. Generate a report with condition scorecards and notable examples.
5. Add tests for dataset integrity and metric calculations.
