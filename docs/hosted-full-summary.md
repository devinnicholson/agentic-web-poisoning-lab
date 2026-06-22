# Hosted Full Matrix Snapshot

Source run: `hosted-20260622T163707Z`

This snapshot summarizes the generated full hosted outputs without checking raw
model rows into Git. The run used Azure OpenAI `gpt-5-mini-2025-08-07` against
all 30 synthetic tasks under A0-A4.

## Scope

| Field | Value |
| --- | --- |
| Hosted rows | 150 |
| Attack rows | 120 |
| Conditions | `A0_DIRECT`, `A1_AGENT_BASELINE`, `A2_SOURCE_RANKING`, `A3_PROMPT_SHIELDS`, `A4_FULL_DEFENSE` |
| Provider errors | 0 |
| Provider blocks | 0 |
| Rows needing retry | 25 |
| Total retries | 25 |
| Prompt tokens | 33,777 |
| Completion tokens | 59,129 |
| Total tokens | 92,906 |
| Posted Azure cost after run | Cost Management still reported `$0.32411925` month-to-date; the full run may not be reflected yet. |

## Condition Scorecard

| Condition | Accuracy | Attack success | Cited poisoned | Filtered poisoned |
| --- | ---: | ---: | ---: | ---: |
| A0_DIRECT | 46.7% | 0.0% | 0.0% | 0.0% |
| A1_AGENT_BASELINE | 96.7% | 4.2% | 80.0% | 0.0% |
| A2_SOURCE_RANKING | 93.3% | 8.3% | 66.7% | 0.0% |
| A3_PROMPT_SHIELDS | 86.7% | 8.3% | 10.0% | 20.0% |
| A4_FULL_DEFENSE | 93.3% | 0.0% | 0.0% | 80.0% |

## Main Findings

- Hosted A1 was usually answer-correct but evidence-compromised: 29/30 answer
  accuracy, but 24/30 rows cited poisoned pages.
- Source ranking alone did not solve source laundering. A2 had 2/24 attack
  successes and still cited poisoned pages in 20/30 rows.
- Prompt Shields sharply reduced poisoned citations, from 24/30 in A1 to 3/30
  in A3, but still left two hosted attack successes.
- Full defense was the cleanest condition: A4 had 0/24 attack successes,
  0/30 poisoned citations, and 24/30 rows with poisoned pages filtered.
- The remaining research issue is abstention calibration. A4 still gave a
  non-abstaining answer on 2/7 `insufficient_evidence` cases.
- Provider reliability was good after retry/backoff: 0 provider errors, 0
  provider blocks, and 25 recovered retries across 150 hosted calls.

## Attack-Class Notes

- A1 cited poisoned evidence in 100% of attack rows for every attack class,
  even when the final answer was correct.
- A2 had visible source-laundering failures: 2/5 source-laundering rows were
  measured attack successes.
- A3 failures concentrated outside the narrow prompt-injection classes: one
  fake-citation-bait row and one stale-page-conflict row were measured attack
  successes.
- A4 eliminated measured attack success and poisoned citations in every attack
  class in this run.

Generated raw outputs remain under `experiments/results/hosted-full/` and are
intentionally ignored by Git. The key generated files are `report.md`,
`comparison.md`, `audit-queue.md`, and `stats.md`.
