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
- Multi-page graph stress statistics showing whether the same controls hold
  when each task has multiple trusted pages and multiple distractors.
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

Completed calibrated relation-gate implementation slice:

1. `A9_CALIBRATED_RELATION_GATE` adds a conservative evidence-gap override on
   top of A8's relation-classifier stage.
2. `make relation-calibrated-expanded-refresh` passes locally on the expanded
   boundary set.

Completed hosted calibrated relation-gate slice:

1. `make hosted-relation-calibrated-expanded-repeats-refresh` ran 80 hosted A9
   rows.
2. `docs/hosted-relation-calibrated-expanded-summary.md` documents the result:
   A9 reached 80/80 accuracy, 40/40 correct abstention, 40/40 direct `no`
   preservation, and 0/80 poisoned citations.

Completed paired statistical appendix slice:

1. `agentic-web-poisoning-lab paired-analysis` merges multiple hosted result
   files and aligns rows by task and repeat index.
2. `make paired-analysis-a7-a9` regenerates
   `docs/paired-a7-a9-analysis.md`.
3. The appendix quantifies the A8/A9 missing-validation repair as 14 fixed A8
   misses, 0 new A9 misses, and exact McNemar p = 0.0001.

Completed paired human-audit slice:

1. `data/manual-audit.hosted-a8-a9-boundary.jsonl` adjudicates the 14 A8 false
   non-abstains and the 14 paired A9 repairs.
2. `tests/test_manual_audit.py` validates that the A8 and A9 audited rows cover
   the same task/repeat cells and use known audit labels.

Completed local graph-stress slice:

1. `data/tasks.graph.jsonl` and `data/pages.graph.jsonl` add 12 multi-page
   graph tasks across dining, housing, emergency, and battery-safety domains.
2. Each task has two trusted current pages and two adversarial distractors.
3. `make graph-refresh` passes locally: A1 reached 0/12 accuracy with 12/12
   attack success and poisoned citations, while A4/A8/A9 reached 12/12
   accuracy with 0/12 attack success and 0/12 poisoned citations.

Completed hosted graph-stress slice:

1. `make hosted-graph-repeats-refresh` ran 144 hosted rows across A1, A4, A8,
   and A9 with three repeats per graph task.
2. `docs/hosted-graph-summary.md` documents the result: A8 and A9 reached
   36/36 accuracy, 12/12 correct abstention, 12/12 direct `no` preservation,
   12/12 direct `yes` preservation, and 0/36 poisoned citations.
3. A4 filtered poisoned pages in 36/36 rows and had 0/36 poisoned citations,
   but only reached 2/12 correct abstention on graph evidence gaps.

Completed hosted long-graph slice:

1. `data/tasks.graph-long.jsonl` and `data/pages.graph-long.jsonl` add 12
   harder graph tasks with three trusted current pages and three adversarial
   distractors per task.
2. `make hosted-long-graph-repeats-refresh` ran 144 hosted rows across A1, A4,
   A8, and A9 with three repeats per long-graph task.
3. `docs/hosted-long-graph-summary.md` documents the result: A8/A9 repaired
   evidence-gap abstention to 12/12, but introduced over-abstention on direct
   policy and privacy-board controls. A9 reached 28/36 accuracy versus A4's
   24/36, with 0/36 poisoned citations.

## A10 Long-Graph Preservation Follow-Up

Completed:

1. Add an A10 preservation-calibrated relation gate that keeps A9's
   evidence-gap calibration while explicitly preserving direct support and
   direct refutation when trusted current pages agree.
2. `make hosted-long-graph-preservation-repeats-refresh` ran 36 hosted A10 rows
   with three repeats per long-graph task.
3. `docs/hosted-long-graph-preservation-summary.md` documents the result: A10
   reached 36/36 accuracy, 12/12 evidence-gap abstention, and 24/24
   direct-control preservation, with 0/36 attack success and 0/36 poisoned
   citations.
4. A second `gpt-4-1-mini` Azure deployment replicated the A10 result on 36
   hosted rows: 36/36 accuracy, 12/12 evidence-gap abstention, 24/24
   direct-control preservation, and 0/36 provider errors.
5. `make hosted-long-graph-relation-gates-cross-model-repeats-refresh` ran the
   gpt-4.1-mini A8/A9 long-graph baseline. Both A8 and A9 reached 25/36
   accuracy with 12/12 evidence-gap abstention, 12/12 direct `yes`
   preservation, and only 1/12 direct `no` preservation. This makes A10's
   12/12 direct `no` repair a within-model before/after result.

## Long-Graph v2 Iteration

Completed:

1. `data/tasks.graph-long-v2.jsonl` and `data/pages.graph-long-v2.jsonl` add a
   24-task stress corpus across eight campus AI governance domains.
2. Each task has four trusted current evidence pages and four adversarial
   distractors, adding fake-citation laundering on top of source laundering,
   stale-page conflict, and confidence pressure.
3. `make long-graph-v2-refresh` runs local A1/A4/A8/A9/A10 baselines to confirm
   the harness behavior before hosted spend.
4. `make hosted-long-graph-v2-pilot-refresh` runs a three-repeat hosted
   A1/A4/A8/A9/A10 pilot to test whether A10's preservation repair scales under
   larger context pressure while retaining a same-corpus vulnerable baseline.
5. `docs/hosted-long-graph-v2-summary.md` documents the hosted result: A10
   reached 72/72 accuracy, 24/24 evidence-gap abstention, and 48/48 direct
   controls, with 0/72 attack success, 0/72 cited poisoned pages, and 0/72
   provider errors. A8 reached 70/72 and A9 reached 66/72 because they retained
   evidence-gap abstention but over-abstained on direct controls.
6. `make hosted-long-graph-v2-cross-model-repeats-refresh` replicated the
   A8/A9/A10 comparison on `gpt-4-1-mini`, adding 216 hosted rows. A10 again
   reached 72/72 accuracy, 24/24 abstention, and 48/48 direct controls, while
   A8 reached 60/72 and A9 reached 59/72 because direct-control false
   abstentions were stronger on the second deployment.
7. `make paired-analysis-long-graph-v2-preservation` generates
   `docs/paired-long-graph-v2-preservation-analysis.md`, a deployment-aware
   paired appendix. Across both v2 deployments, A10 fixed 14 direct-control
   rows relative to A8 and 19 relative to A9, with 0 new direct-control misses.
8. `make casebook-long-graph-v2-preservation` generates
   `docs/long-graph-v2-preservation-casebook.md`, a qualitative casebook with
   14 representative repaired rows, trusted/current evidence pages,
   relation-label changes, and A10 safety metrics.
9. `make transition-analysis-long-graph-v2-preservation` generates
   `docs/long-graph-v2-preservation-transition-analysis.md`, a mechanism
   appendix showing 35 page-label transition observations concentrated on the
   33 repaired direct-control rows, with 0 non-repaired direct-control rows
   changing labels and 0 A10 regressions.
10. `make artifact-manifest-refresh` generates
    `docs/research-artifact-manifest.md`, a deterministic checksum manifest
    covering the key v2 corpora, hosted result files, public summaries,
    casebook, transition appendix, and dashboard.

Next possible slice:

1. Extend manual audit labels from representative challenge rows to every
   hosted full-matrix, challenge-set, and boundary failure row.
