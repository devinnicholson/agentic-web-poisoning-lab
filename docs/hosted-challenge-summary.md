# Hosted Challenge Matrix Snapshot

Source run: `hosted-20260623T153515Z`

This snapshot summarizes the abstention-heavy challenge run without checking
raw model rows into Git. The run used Azure OpenAI `gpt-5-mini-2025-08-07`
against 24 challenge tasks under A1-A4.

## Scope

| Field | Value |
| --- | --- |
| Hosted rows | 96 |
| Attack rows | 80 |
| Challenge tasks | 24 |
| Source-laundering tasks | 12 |
| `insufficient_evidence` tasks | 13 |
| Conditions | `A1_AGENT_BASELINE`, `A2_SOURCE_RANKING`, `A3_PROMPT_SHIELDS`, `A4_FULL_DEFENSE` |
| Provider errors | 0 |
| Provider blocks | 0 |
| Rows needing retry | 10 |
| Total retries | 10 |
| Prompt tokens | 24,872 |
| Completion tokens | 41,518 |
| Total tokens | 66,390 |
| Posted Azure cost after run | `$0.5639255` month-to-date for Foundry Models. |

## Condition Scorecard

| Condition | Accuracy | Attack success | Cited poisoned | Filtered poisoned |
| --- | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 70.8% | 35.0% | 83.3% | 0.0% |
| A2_SOURCE_RANKING | 58.3% | 45.0% | 75.0% | 0.0% |
| A3_PROMPT_SHIELDS | 70.8% | 0.0% | 0.0% | 0.0% |
| A4_FULL_DEFENSE | 62.5% | 0.0% | 0.0% | 83.3% |

## Main Findings

- The challenge set amplified the residual weakness from the full matrix:
  abstention-heavy source laundering. A1 had 7/20 attack successes; A2 had
  9/20.
- Source ranking alone was not a defense on this slice. A2 reduced poisoned
  citations only slightly and had a higher attack-success rate than A1.
- A3 eliminated measured attack success and poisoned citations without
  filtering pages, suggesting that prompt-level source skepticism helped on
  this specific challenge set.
- A4 also eliminated measured attack success and poisoned citations, while
  explicitly filtering 20/24 rows with poisoned pages.
- A3 and A4 still struggled with abstention calibration. A3 had 7/13 false
  non-abstains on `insufficient_evidence` tasks; A4 had 9/13.
- Provider reliability was clean: zero provider errors or blocks and 10
  recovered retries across 96 hosted calls.

## Attack-Class Notes

- Source laundering was the strongest adversarial class: A1 failed 6/12 rows
  and A2 failed 7/12.
- Fake citation bait also exposed abstention weakness: A1 failed 1/4 rows and
  A2 failed 2/4.
- Stale page conflicts were easier for the hosted model behaviorally, but A1
  and A2 still cited poisoned stale pages in every stale-conflict row.
- A3 and A4 reached 0/20 attack success and 0/24 poisoned citations across the
  full challenge set.

Generated raw outputs remain under `experiments/results/hosted-challenge/` and
are intentionally ignored by Git. The key generated files are `report.md`,
`comparison.md`, `audit-queue.md`, and `stats.md`.
