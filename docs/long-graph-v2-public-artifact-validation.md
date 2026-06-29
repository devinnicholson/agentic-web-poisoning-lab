# Long-Graph v2 Public Artifact Validation

This deterministic report validates that the committed public v2 row snapshots are internally consistent, redacted, and referentially linked to the committed synthetic corpus.

## Sources

- Tasks: `data/tasks.graph-long-v2.jsonl`
- Pages: `data/pages.graph-long-v2.jsonl`
- Results: `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl`
- Summary: `artifacts/long-graph-v2/hosted-gpt5-mini-summary.json`
- Results: `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl`
- Summary: `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-summary.json`

## Corpus Checks

| Check | Result | Detail |
| --- | --- | --- |
| Task IDs unique | PASS | 24 tasks |
| Page IDs unique | PASS | 128 pages |
| Task required pages exist | PASS | all required page IDs resolve |

## Snapshot Checks

| Snapshot | Rows | Summary match | Redaction check | Condition coverage | Unknown task IDs | Unknown page IDs |
| --- | ---: | --- | --- | --- | ---: | ---: |
| Primary hosted gpt-5-mini snapshot | 360 | PASS | PASS | PASS | 0 | 0 |
| Cross-model gpt-4.1-mini snapshot | 216 | PASS | PASS | PASS | 0 | 0 |

## Condition Counts

| Snapshot | Condition | Expected rows | Observed rows |
| --- | --- | ---: | ---: |
| Primary hosted gpt-5-mini snapshot | `A1_AGENT_BASELINE` | 72 | 72 |
| Primary hosted gpt-5-mini snapshot | `A4_FULL_DEFENSE` | 72 | 72 |
| Primary hosted gpt-5-mini snapshot | `A8_CLASSIFIED_RELATION_GATE` | 72 | 72 |
| Primary hosted gpt-5-mini snapshot | `A9_CALIBRATED_RELATION_GATE` | 72 | 72 |
| Primary hosted gpt-5-mini snapshot | `A10_PRESERVATION_CALIBRATED_GATE` | 72 | 72 |
| Cross-model gpt-4.1-mini snapshot | `A8_CLASSIFIED_RELATION_GATE` | 72 | 72 |
| Cross-model gpt-4.1-mini snapshot | `A9_CALIBRATED_RELATION_GATE` | 72 | 72 |
| Cross-model gpt-4.1-mini snapshot | `A10_PRESERVATION_CALIBRATED_GATE` | 72 | 72 |

## Issues

- PASS: no validation issues found.
