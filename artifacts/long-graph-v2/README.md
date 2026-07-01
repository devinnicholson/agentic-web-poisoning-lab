# Long-Graph v2 Public Artifact Package

This directory contains the committed public row snapshots for the long-graph v2
preservation finding. The snapshots are derived from hosted Azure OpenAI runs,
but provider-only identifiers are redacted so the files can be reviewed in a
public repository.

## Files

| File | Contents |
| --- | --- |
| `hosted-gpt5-mini-results.jsonl` | Primary hosted run: A1, A4, A8, A9, and A10 over 24 tasks and 3 repeats. |
| `hosted-gpt5-mini-summary.json` | Summary metrics recomputed from the primary public rows. |
| `hosted-gpt41-mini-a8-a10-results.jsonl` | Cross-model replication: A8, A9, and A10 over the same 24 tasks and 3 repeats. |
| `hosted-gpt41-mini-a8-a10-summary.json` | Summary metrics recomputed from the cross-model public rows. |
| `blind-audit-queue.jsonl` | Condition-blinded evidence-review queue generated from all 576 public rows. |
| `blind-audit-key.jsonl` | Unblinding key joining audit IDs back to task, condition, deployment, answer, and metric fields. |

## Row Schema

Each JSONL row is one task, condition, and repeat. The fields used by the public
analyses are:

| Field | Meaning |
| --- | --- |
| `task_id` | Synthetic task identifier from `data/tasks.graph-long-v2.jsonl`. |
| `condition` | Defense condition, such as `A8_CLASSIFIED_RELATION_GATE` or `A10_PRESERVATION_CALIBRATED_GATE`. |
| `repeat_index` | Hosted repeat number for paired tests and stability checks. |
| `expected_answer`, `actual_answer` | Ground-truth label and model-produced final label. |
| `selected_page_ids`, `cited_page_ids`, `filtered_page_ids`, `visited_page_ids` | Evidence path through the synthetic web corpus. |
| `metrics` | Per-row scoring flags used by summaries, paired analysis, and validation. |
| `safety_flags` | Defense mechanisms enabled or triggered for the row. |
| `provider_metadata` | Model/deployment metadata, usage, retry counts, and latency checkpoints. |
| `public_snapshot_redactions` | Redacted provider fields, when present. |

## Redactions

The public snapshot command replaces these provider-only fields with
`redacted_for_public_snapshot`:

| Redacted field | Reason |
| --- | --- |
| `provider_metadata.endpoint_host` | Azure resource hostname is not needed to reproduce analysis. |
| `provider_metadata.response_id` | Provider request identifier is not needed for public review. |
| `provider_metadata.system_fingerprint` | Provider service fingerprint is not needed for public review. |

No API keys, bearer tokens, or environment variables are written by the hosted
harness.

## Rebuild

From a local checkout that still has the private hosted output directories:

```bash
make public-snapshot-long-graph-v2
make blind-audit-long-graph-v2-public
make validate-blind-audit-long-graph-v2
make validate-long-graph-v2-public-artifacts
make artifact-manifest-refresh
```

The committed public snapshot validation report is
`docs/long-graph-v2-public-artifact-validation.md`; the blind-audit validation
report is `docs/blind-audit-validation.md`; the checksum manifest is
`docs/research-artifact-manifest.md`.
