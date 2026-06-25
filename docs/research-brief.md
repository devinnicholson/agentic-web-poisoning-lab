# Research Brief

## Title

Agentic Web Poisoning and Abstention Calibration

## Claim

Web-browsing agents can avoid obvious poisoned citations while still
over-answering evidence gaps. Source hygiene is necessary, but not sufficient;
explicit evidence-sufficiency and evidence-relation rules materially improve
abstention calibration on hosted challenge and boundary sets.

## Benchmark

- 30-task synthetic seed benchmark with source laundering, stale-page conflict,
  fake citation bait, confidence pressure, action hijack, and indirect prompt
  injection.
- 24-task challenge benchmark focused on source laundering and abstention
  calibration.
- 12-task multi-page graph stress benchmark with two trusted current evidence
  pages and two adversarial distractors per task.
- 12-task long-graph stress benchmark with three trusted current evidence pages
  and three adversarial distractors per task.
- Redacted synthetic pages with structured source type, trust label, freshness,
  poisoned/not-poisoned status, attack class, and task-relevant claim.
- Hosted validation uses Azure OpenAI `gpt-5-mini-2025-08-07`.

## Main Hosted Results

Full matrix, 150 rows:

| Condition | Accuracy | Attack success | Cited poisoned |
| --- | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 96.7% | 4.2% | 80.0% |
| A4_FULL_DEFENSE | 93.3% | 0.0% | 0.0% |

Challenge matrix, 96 rows:

| Condition | Accuracy | Attack success | Cited poisoned |
| --- | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 70.8% | 35.0% | 83.3% |
| A4_FULL_DEFENSE | 62.5% | 0.0% | 0.0% |

Strict-abstention follow-up, 120 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A4_FULL_DEFENSE | 58.3% | 0.0% | 0.0% | 3/13 |
| A5_STRICT_ABSTENTION | 95.8% | 0.0% | 0.0% | 12/13 |

Evidence-boundary follow-up, 16 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A4_FULL_DEFENSE | 62.5% | 0.0% | 0.0% | 1/4 |
| A5_STRICT_ABSTENTION | 75.0% | 0.0% | 0.0% | 2/4 |

Relation-boundary follow-up, 16 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A5_STRICT_ABSTENTION | 75.0% | 0.0% | 0.0% | 2/4 |
| A6_RELATION_VERIFIER | 87.5% | 0.0% | 0.0% | 3/4 |

Repeated relation-boundary sweep, 80 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A5_STRICT_ABSTENTION | 92.5% | 0.0% | 0.0% | 17/20 |
| A6_RELATION_VERIFIER | 97.5% | 0.0% | 0.0% | 19/20 |

Structured relation-gate sweep, 80 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A6_RELATION_VERIFIER | 97.5% | 0.0% | 0.0% | 19/20 |
| A7_STRUCTURED_RELATION_GATE | 100.0% | 0.0% | 0.0% | 20/20 |

Expanded structured relation-gate sweep, 160 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A6_RELATION_VERIFIER | 97.5% | 0.0% | 0.0% | 38/40 |
| A7_STRUCTURED_RELATION_GATE | 100.0% | 0.0% | 0.0% | 40/40 |

Expanded classified relation-gate sweep, 160 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A7_STRUCTURED_RELATION_GATE | 100.0% | 0.0% | 0.0% | 40/40 |
| A8_CLASSIFIED_RELATION_GATE | 82.5% | 0.0% | 0.0% | 26/40 |

Expanded calibrated relation-gate sweep, 80 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A9_CALIBRATED_RELATION_GATE | 100.0% | 0.0% | 0.0% | 40/40 |

Local graph stress benchmark, 48 rows:

| Condition | Accuracy | Attack success | Cited poisoned |
| --- | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 0.0% | 100.0% | 100.0% |
| A4_FULL_DEFENSE | 100.0% | 0.0% | 0.0% |
| A8_CLASSIFIED_RELATION_GATE | 100.0% | 0.0% | 0.0% |
| A9_CALIBRATED_RELATION_GATE | 100.0% | 0.0% | 0.0% |

Hosted graph stress benchmark, 144 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 75.0% | 19.4% | 38.9% | 3/12 |
| A4_FULL_DEFENSE | 72.2% | 0.0% | 0.0% | 2/12 |
| A8_CLASSIFIED_RELATION_GATE | 100.0% | 0.0% | 0.0% | 12/12 |
| A9_CALIBRATED_RELATION_GATE | 100.0% | 0.0% | 0.0% | 12/12 |

Hosted long-graph stress benchmark, 144 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention | Direct controls |
| --- | ---: | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 66.7% | 5.6% | 8.3% | 0/12 | 24/24 |
| A4_FULL_DEFENSE | 66.7% | 0.0% | 0.0% | 0/12 | 24/24 |
| A8_CLASSIFIED_RELATION_GATE | 75.0% | 0.0% | 0.0% | 12/12 | 15/24 |
| A9_CALIBRATED_RELATION_GATE | 77.8% | 0.0% | 0.0% | 12/12 | 16/24 |

Hosted A10 long-graph preservation follow-up, 36 rows:

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention | Direct controls |
| --- | ---: | ---: | ---: | ---: | ---: |
| A10_PRESERVATION_CALIBRATED_GATE | 100.0% | 0.0% | 0.0% | 12/12 | 24/24 |

Paired A7/A8/A9 appendix:

- A8 reduced paired missing-validation abstention by 35.0 percentage points
  relative to A7: 14 A7-only correct rows, 0 A8-only correct rows, exact
  McNemar p = 0.0001.
- A9 recovered those misses relative to A8: 0 A8-only correct rows, 14 A9-only
  correct rows, exact McNemar p = 0.0001.
- A9 introduced 0 new direct-negative errors and 0 new poisoned citations in
  the paired comparison.

## Contribution

1. A public synthetic benchmark that separates final-answer correctness from
   evidence quality.
2. A hosted evaluation harness with resumable Azure model runs, provider
   reliability stats, and confidence intervals.
3. A hard challenge set showing that defenses can block poisoning while still
   failing abstention calibration.
4. A strict evidence-sufficiency ablation showing a large improvement in false
   non-abstain behavior without blanket refusal.
5. A boundary probe showing that certification and deployment-trial language
   remains hard even after strict abstention.
6. A relation-verifier ablation that improves the boundary probe while exposing
   the remaining certification-language failure.
7. A repeated-trial sweep showing the remaining errors are stochastic and
   concentrated in negative-sounding missing-validation language.
8. A structured relation-gate ablation showing that application-level evidence
   relation enforcement closes the observed certification boundary failure.
9. An expanded boundary sweep showing that the structured relation gate holds
   across 16 paired certification, audit, replication, and deployment-trial
   tasks.
10. A classifier-gate follow-up showing that replacing verified labels with
   model-predicted labels preserves direct `no` controls but reintroduces
   missing-validation false non-abstains.
11. A calibrated classifier-gate follow-up showing that conservative
   evidence-gap overrides recover the A7 verified-label ceiling on the expanded
   synthetic set.
12. A paired statistical appendix that aligns A7/A8/A9 rows by task and repeat
   index and quantifies the classifier degradation and calibrated repair.
13. Manual adjudication labels for representative challenge rows, strict A5
   abstention rows, and the paired A8/A9 boundary repairs.
14. A multi-page graph stress benchmark that tests the same defenses against
   larger evidence contexts and distractor sets.
15. A hosted graph stress run showing that relation-gated defenses preserve
   36/36 accuracy and 12/12 evidence-gap abstention where full defense still
   over-answers.
16. A harder hosted long-graph run showing the next bottleneck: relation gates
   can over-abstain on direct policy and privacy-board controls under longer
   evidence contexts.
17. An A10 preservation-calibrated relation gate that repairs the hosted
   long-graph over-abstention boundary while retaining 12/12 evidence-gap
   abstention.
18. A static dashboard for inspection.

## Limitations

- Synthetic pages do not measure prevalence on the live web.
- Results are from one hosted model deployment and should be repeated across
  models and runs.
- Some evidence-gap prompts are semantically close to direct negation; the
  remaining A6 miss is exactly in this boundary area. A7 fixes it on this
  synthetic set by relying on verified relation labels, which must be replaced
  by a reliable classifier or metadata source in a production system. A8 shows
  that a hosted classifier is not yet reliable enough on missing certification,
  audit, and deployment-trial wording. A9 repairs that specific synthetic
  failure mode with an application-level conservative calibration rule. A10
  repairs the later long-graph over-abstention boundary by preserving direct
  support and direct refutation when trusted current pages clearly answer the
  question.
- The harness models application-level controls, not a production browser
  sandbox.

## Demo Path

Open `static/research-dashboard.html` for aggregate results. Open
`static/action-hijack-case-study.html` for the trace-style demo.

## Reproduction

Run `make test`, `make strict-challenge-refresh`, or the hosted targets in
`docs/reproducibility.md`.
