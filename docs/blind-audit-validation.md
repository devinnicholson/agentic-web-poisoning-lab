# Long-Graph v2 Blind Audit Validation

This deterministic report validates that the committed blinded audit queue is aligned with the public row snapshots while keeping the reviewer-facing packet free of configured condition, task, page, metric, and provider leaks.

## Sources

- Blind queue: `artifacts/long-graph-v2/blind-audit-queue.jsonl`
- Unblinding key: `artifacts/long-graph-v2/blind-audit-key.jsonl`
- Source rows: `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl`
- Source rows: `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl`

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| Queue row count | PASS | 576 queue rows; 576 source rows |
| Key row count | PASS | 576 key rows; 576 source rows |
| Queue audit IDs unique | PASS | all queue audit IDs unique |
| Key audit IDs unique | PASS | all key audit IDs unique |
| Queue/key ID sets match | PASS | queue and key ID sets match |
| Key covers source rows | PASS | key and source ID sets match |
| Key source pointers match source rows | PASS | all key source pointers match |
| Reviewer labels are empty | PASS | all review label slots are null |
| Page aliases are local and cited refs resolve | PASS | all page aliases and citations resolve |
| Queue does not expose key-only fields | PASS | no forbidden structured keys found |
| Forbidden leakage scan | PASS | no configured leakage strings found |

## Coverage

| Item | Count |
| --- | ---: |
| Source rows | 576 |
| Blind queue rows | 576 |
| Unblinding key rows | 576 |
| Queue unique audit IDs | 576 |
| Key unique audit IDs | 576 |

## Issues

- PASS: no validation issues found.
