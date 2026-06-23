# Project Plan

## Goal

Create a credible, low-cost research artifact showing how web-browsing agents
fail or recover when pages contain adversarial or misleading content.

## Research Outputs

- Synthetic web-page dataset with page trust, freshness, and attack labels.
- Local deterministic harness for repeatable failures.
- Hosted Azure validation with a real model once local behavior is stable.
- Full hosted matrix statistics with confidence intervals and paired defense
  deltas.
- Human audit queue for source selection, citation support, abstention quality,
  and action safety.
- Static demo showing a single task across A1, A3, and A4.

## Milestones

| Milestone | Output | Success Criterion |
| --- | --- | --- |
| M0 scaffold | Repo, protocol, seed data | Project can be reviewed without extra context. |
| M1 local harness | CLI runs seed cases under A0-A4 | Deterministic report shows at least one baseline failure. |
| M2 dataset expansion | 30-50 synthetic tasks | Complete at 30 tasks: 24 adversarial tasks and 6 benign controls. |
| M3 audit workflow | Markdown audit queue | Complete locally: provider blocks, bad citations, and unsafe actions are reviewable. |
| M4 hosted validation | Azure-backed run | Full 150-row hosted matrix complete; raw hosted outputs stay out of Git. |
| M5 demo artifact | Static HTML trace | First trace complete: five-minute action-hijack demo works without credentials. |

## Engineering Approach

- Keep page parsing structured. Store page metadata, body summary, trust label,
  freshness, and attack class separately.
- Treat a provider block or refusal as an outcome, not a crash.
- Separate answer correctness from source quality and action safety.
- Redact raw attack text in public docs and demos.
- Reuse the RAG lab's discipline: generated outputs stay under
  `experiments/results/` and out of Git.

## First Implementation Slice

Status: complete for the 30-task local dataset.

Implemented:

- Schema objects for task cases, web pages, agent traces, and metrics.
- Deterministic local browsing agent.
- A0-A4 conditions with source ranking, Prompt Shields-style filtering, and
  full-defense filtering.
- Markdown report with condition scorecards and notable examples.
- Unit tests for dataset integrity, attack-class balance, behavior, reporting,
  and CLI outputs.

Completed local artifact slice:

1. Human audit queue for source-selection and citation-quality review.
2. Static action-hijack trace for the clearest baseline-failure/full-defense
   pair.

Completed hosted research slice:

1. `make hosted-full-refresh` ran the 30-task, five-condition hosted matrix.
2. `experiments/results/hosted-full/stats.md` now includes condition-level
   confidence intervals, attack-class rates, and paired defense deltas.
3. `docs/hosted-full-summary.md` promotes the aggregate findings while keeping
   raw hosted rows out of Git.

Next implementation slice:

1. Add manual audit labels for hosted full-matrix and challenge-set failure
   rows.
2. Turn the summaries into a paper-style abstract, threat model, limitations,
   and results section.
3. Decide whether to run a second model or a repeated-trial sweep for variance.
