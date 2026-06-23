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
7. Manual adjudication labels and a static dashboard for inspection.

## Limitations

- Synthetic pages do not measure prevalence on the live web.
- Results are from one hosted model deployment and should be repeated across
  models and runs.
- Some evidence-gap prompts are semantically close to direct negation; the
  remaining A6 miss is exactly in this boundary area.
- The harness models application-level controls, not a production browser
  sandbox.

## Demo Path

Open `static/research-dashboard.html` for aggregate results. Open
`static/action-hijack-case-study.html` for the trace-style demo.

## Reproduction

Run `make test`, `make strict-challenge-refresh`, or the hosted targets in
`docs/reproducibility.md`.
