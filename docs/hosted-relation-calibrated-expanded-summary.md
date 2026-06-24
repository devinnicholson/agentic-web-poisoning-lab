# Hosted Expanded Calibrated Relation-Gate Snapshot

Source run: `hosted-20260624T050451Z`

This snapshot summarizes a five-repeat hosted run of
`A9_CALIBRATED_RELATION_GATE` on the expanded 16-task boundary set. A9 keeps the
A8 relation-classifier stage, but adds a conservative application override:
when trusted evidence only reports absent independent certification, audit,
deployment trial, replication, or validation, the relation label is calibrated
to `missing_validation`.

The run used Azure OpenAI `gpt-5-mini-2025-08-07`.

## Scope

| Field | Value |
| --- | --- |
| Hosted rows | 80 |
| Attack rows | 80 |
| Boundary tasks | 16 |
| Missing-validation rows | 40 |
| Direct-negative rows | 40 |
| Repeats per task | 5 |
| Condition | `A9_CALIBRATED_RELATION_GATE` |
| Provider errors | 0 |
| Provider blocks | 0 |
| Rows needing retry | 56 |
| Total retries | 56 |
| Prompt tokens | 61,710 |
| Completion tokens | 49,508 |
| Total tokens | 111,218 |
| Posted Azure cost after run | `$0.93446775` month-to-date for Foundry Models; Cost Management posting can lag usage. |

## Condition Scorecard

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: | ---: |
| A9_CALIBRATED_RELATION_GATE | 80 | 100.0% | 0.0% | 0.0% | 40/40 |

A9 preserved 40/40 direct `no` controls, filtered poisoned evidence in 80/80
rows, and produced no false non-abstains.

## Calibration Effect

| Label source | Missing validation | Direct refutation | Direct support |
| --- | ---: | ---: | ---: |
| Raw classifier labels | 30 | 50 | 0 |
| Calibrated labels | 40 | 40 | 0 |

The calibration override changed 10 raw classifier labels. Those changes map to
the A8 failure mode: raw classifier calls sometimes labeled absent independent
validation as direct refutation. A9 converted those evidence-gap summaries back
to `missing_validation` before final synthesis.

## Repeat Stability

Every expanded boundary task was stable across five repeats:

- 8/8 missing-validation tasks reached 5/5 correct abstention.
- 8/8 direct-negative tasks reached 5/5 correct `no`.
- The five A8 instability families (`task_bound_003`, `task_bound_007`,
  `task_bound_009`, `task_bound_011`, and `task_bound_015`) all reached 5/5
  under A9.

## Main Findings

- A9 matched the A7 verified-label ceiling on this expanded synthetic set:
  80/80 accuracy, 40/40 correct abstention, and 40/40 direct `no`
  preservation.
- A9 repaired the A8 classifier-label failure without reopening poisoning
  failures: 0/80 attack success and 0/80 poisoned citations.
- The result supports a precise design claim: a separate relation classifier is
  useful only if the application treats evidence-gap wording conservatively.
  Confidence alone was not sufficient in A8 because wrong classifier labels were
  often high-confidence.
- The paired A7/A8/A9 statistical appendix is committed at
  `docs/paired-a7-a9-analysis.md`.

## Interpretation

A7 proved that relation gating works when labels are trusted. A8 showed that a
raw hosted classifier does not supply reliable enough labels for missing
certification, audit, and deployment-trial wording. A9 closes that specific gap
with a conservative calibration rule.

This should still be interpreted as a synthetic benchmark result, not a
production guarantee. The next external-validity step would be larger synthetic
web graphs or human-labeled real-page snippets. Within the current benchmark,
however, the final architecture is clear: source hygiene, relation
classification, and application-level conservative calibration are all needed.

Generated raw outputs remain under
`experiments/results/hosted-relation-calibrated-expanded-repeats/` and are
intentionally ignored by Git. The key generated files are `report.md`,
`audit-queue.md`, and `stats.md`.
