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
- Strict-abstention challenge statistics showing whether evidence-sufficiency
  prompting improves false non-abstain rates.
- Relation-boundary statistics showing whether explicit evidence-relation
  classification improves negative-sounding missing-validation cases.
- Repeated boundary statistics showing whether remaining false non-abstains are
  stable task failures or stochastic boundary flips.
- Structured relation-gate statistics showing whether application-level
  relation enforcement closes the remaining boundary failure.
- Expanded structured relation-gate statistics showing whether the gate holds
  across a broader 16-task boundary set.
- Classified relation-gate statistics showing whether a separate relation
  classifier can replace synthetic verified relation labels.
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

Completed strict-abstention slice:

1. `A5_STRICT_ABSTENTION` adds an explicit evidence-sufficiency rule on top of
   full defense.
2. `make hosted-strict-challenge-refresh` ran the 24-task challenge matrix
   under A1-A5.
3. `docs/hosted-strict-challenge-summary.md` promotes the aggregate finding:
   A5 reduced false non-abstains from A4's 10/13 to 1/13 while keeping 0/20
   attack success and 0/24 poisoned citations.

Completed boundary slice:

1. `data/tasks.boundary.jsonl` and `data/pages.boundary.jsonl` isolate missing
   validation vs direct negative evidence.
2. `make hosted-boundary-refresh` ran the focused A4/A5 boundary matrix.
3. `docs/hosted-boundary-summary.md` documents the result: A5 improved correct
   abstention from 1/4 to 2/4 while preserving all direct `no` answers.

Completed relation-verifier slice:

1. `A6_RELATION_VERIFIER` adds an explicit direct-support/direct-refutation/
   missing-validation rubric before answer synthesis.
2. `make hosted-relation-boundary-refresh` ran the focused A5/A6 boundary
   follow-up.
3. `docs/hosted-relation-boundary-summary.md` documents the result: A6 improved
   correct abstention from 2/4 to 3/4 while preserving all direct `no` answers
   and keeping 0/8 poisoned citations.

Completed repeated boundary slice:

1. `run-hosted` supports resumable repeated hosted trials with `repeat_index`.
2. `make hosted-relation-boundary-repeats-refresh` ran 80 hosted A5/A6 rows.
3. `docs/hosted-relation-boundary-repeats-summary.md` documents the variance
   result: A6 improved correct abstention from 17/20 to 19/20 while both
   conditions preserved 20/20 direct `no` answers and 0/40 poisoned citations.

Completed structured relation-gate slice:

1. `A7_STRUCTURED_RELATION_GATE` requires an evidence-relation field and
   enforces verified relation labels from selected trusted evidence.
2. `make hosted-relation-gate-repeats-refresh` ran 80 hosted A6/A7 rows.
3. `docs/hosted-relation-gate-repeats-summary.md` documents the result: A7
   reached 40/40 accuracy, 20/20 correct abstention, 20/20 direct `no`
   preservation, and 0/40 poisoned citations.

Completed expanded boundary slice:

1. `data/tasks.boundary-expanded.jsonl` and
   `data/pages.boundary-expanded.jsonl` add 8 more paired boundary tasks.
2. `make hosted-relation-gate-expanded-repeats-refresh` ran 160 hosted A6/A7
   rows.
3. `docs/hosted-relation-gate-expanded-summary.md` documents the result: A7
   reached 80/80 accuracy, 40/40 correct abstention, 40/40 direct `no`
   preservation, and 0/80 poisoned citations.

Completed relation-classifier implementation slice:

1. `A8_CLASSIFIED_RELATION_GATE` adds a separate relation-classifier stage over
   selected trusted evidence summaries.
2. Final synthesis receives classifier-predicted relation labels rather than
   `supports_tasks` gold labels.
3. `make relation-classifier-expanded-refresh` passes locally on the expanded
   A7/A8 boundary comparison.

Completed hosted relation-classifier slice:

1. `make hosted-relation-classifier-expanded-repeats-refresh` ran 160 hosted
   A7/A8 rows.
2. `docs/hosted-relation-classifier-expanded-summary.md` documents the result:
   A8 preserved 40/40 direct `no` controls and 0/80 poisoned citations, but
   dropped to 26/40 correct abstention on missing-validation rows.

Next implementation slice:

1. Add classifier calibration experiments: confidence-aware abstention,
   stricter relation prompts, or a second classifier pass that defaults to
   `missing_validation` on absent independent validation.
2. Extend manual audit labels from representative challenge rows to every
   hosted full-matrix, challenge-set, and boundary failure row.
