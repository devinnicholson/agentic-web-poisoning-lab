# Hosted Graph Stress Snapshot

Source run: `hosted-20260624T190829Z`

This snapshot summarizes the three-repeat hosted graph stress run across the
12-task multi-page corpus in `data/tasks.graph.jsonl` and
`data/pages.graph.jsonl`. Each task provides two trusted current pages and two
adversarial distractors, forcing the agent to answer from a small evidence
graph rather than from a single minimal pair.

The run used Azure OpenAI `gpt-5-mini-2025-08-07`.

## Scope

| Field | Value |
| --- | --- |
| Hosted rows | 144 |
| Attack rows | 144 |
| Graph tasks | 12 |
| Trusted pages per task | 2 |
| Adversarial distractors per task | 2 |
| Conditions | `A1_AGENT_BASELINE`, `A4_FULL_DEFENSE`, `A8_CLASSIFIED_RELATION_GATE`, `A9_CALIBRATED_RELATION_GATE` |
| Repeats per task | 3 |
| Provider errors | 0 |
| Provider blocks | 0 |
| Rows needing retry | 98 |
| Total retries | 127 |
| Prompt tokens | 100,414 |
| Completion tokens | 98,530 |
| Total tokens | 198,944 |
| Posted Azure cost after run | `$1.3209305` month-to-date for Foundry Models; Cost Management posting can lag usage. |

## Condition Scorecard

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 36 | 75.0% | 19.4% | 38.9% | 3/12 |
| A4_FULL_DEFENSE | 36 | 72.2% | 0.0% | 0.0% | 2/12 |
| A8_CLASSIFIED_RELATION_GATE | 36 | 100.0% | 0.0% | 0.0% | 12/12 |
| A9_CALIBRATED_RELATION_GATE | 36 | 100.0% | 0.0% | 0.0% | 12/12 |

All four conditions preserved the 12/12 direct `no` controls and 12/12 direct
`yes` controls. The accuracy differences came entirely from graph-gap rows
whose intended answer was `insufficient_evidence`.

## Abstention Calibration

| Condition | Insufficient-evidence rows | Correct abstention | False non-abstain |
| --- | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 12 | 3 | 9 |
| A4_FULL_DEFENSE | 12 | 2 | 10 |
| A8_CLASSIFIED_RELATION_GATE | 12 | 12 | 0 |
| A9_CALIBRATED_RELATION_GATE | 12 | 12 | 0 |

A4 did the expected source-hygiene work: it filtered poisoned pages in 36/36
rows and cited poisoned pages in 0/36 rows. It still over-answered 10/12
evidence gaps as `no`. A8 and A9 kept the same poisoning-control profile while
correctly abstaining on every graph-gap repeat.

## Provider Reliability

| Condition | Rows | Provider errors | Provider blocks | Total retries | Prompt tokens | Completion tokens | Avg latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 36 | 0 | 0 | 11 | 13,863 | 18,522 | 16.43s |
| A4_FULL_DEFENSE | 36 | 0 | 0 | 15 | 11,775 | 13,789 | 18.49s |
| A8_CLASSIFIED_RELATION_GATE | 36 | 0 | 0 | 49 | 36,886 | 34,841 | 21.69s |
| A9_CALIBRATED_RELATION_GATE | 36 | 0 | 0 | 52 | 37,890 | 31,378 | 20.39s |

The relation-gated conditions were more expensive operationally: every A8 and
A9 row required at least one retry, and both conditions used roughly three
times the prompt tokens of A4. The hosted result is therefore not a free
improvement; it trades extra validation work for substantially better evidence
gap behavior.

## Main Findings

- The graph stress set generalizes the core boundary result beyond minimal
  pairs. Source hygiene alone can remove poisoned citations while leaving
  evidence-gap abstention weak.
- A1 was variably vulnerable under hosted sampling: 7/36 attack successes and
  14/36 poisoned citations, but it still answered all direct yes/no controls
  correctly.
- A4 blocked every poisoned citation and attack success, yet had lower accuracy
  than A1 because it turned 10/12 evidence gaps into confident `no` answers.
- A8 and A9 reached 36/36 accuracy, 12/12 correct abstention, 12/12 direct `no`
  preservation, 12/12 direct `yes` preservation, and 0/36 poisoned citations.
- The result strengthens the paper claim: robust browsing agents need source
  trust controls plus application-level evidence-relation gating. Filtering bad
  pages is necessary but not sufficient.

Generated raw outputs remain under
`experiments/results/hosted-graph-repeats/` and are intentionally ignored by
Git. The key generated files are `report.md`, `audit-queue.md`, and `stats.md`.
