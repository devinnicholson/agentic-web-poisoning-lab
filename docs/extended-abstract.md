# Preserving Useful Answers Under Agentic Web Poisoning

## Abstract

Agentic retrieval systems are often evaluated on whether they avoid poisoned or
stale web evidence, but a defense that simply abstains whenever evidence looks
messy can be unusable. This project studies that tradeoff on a synthetic
campus AI-governance web corpus where each task contains trusted current pages
and adversarial distractors such as source-laundered claims, stale-page
conflicts, confidence pressure, and fake citations. Across 576 committed hosted
rows from two Azure OpenAI deployments, the A10 preservation-calibrated relation
gate preserved correct abstention on all paired evidence-gap rows while
repairing direct-control over-abstention introduced by earlier relation gates.

In the primary `gpt-5-mini` run, A8 and A9 blocked attack success and preserved
all 24 evidence-gap abstentions, but answered only 46/48 and 42/48 direct
controls correctly. A10 answered 72/72 rows correctly, including 48/48 direct
controls, with 0/72 attack successes, 0/72 poisoned citations, and 0/72 provider
errors. In the `gpt-4.1-mini` replication, A8 and A9 again preserved 24/24
evidence-gap abstentions but fell to 36/48 and 35/48 direct controls; A10 again
answered 72/72 rows correctly with 48/48 direct controls and no attack success.
Paired across both deployments, A10 fixed 14 direct-control rows relative to A8
and 19 relative to A9, with 0 new direct-control misses; exact McNemar tests on
direct controls were p = 0.0001 for A8 to A10 and p < 0.0001 for A9 to A10.

## Method Summary

The long-graph v2 corpus contains 24 tasks across 8 campus AI-governance
domains. Each task has 4 trusted current evidence pages and 4 adversarial
distractor pages. The hosted evaluation compares baseline browsing and
defensive conditions that add page screening, source ranking, relation
classification, calibration, and preservation logic. Public rows are sanitized
to redact provider-only identifiers while retaining row-level evidence paths,
metrics, model metadata, retry counts, and token usage needed for review.

## Main Claim

The central empirical claim is not that A10 is universally robust. It is that,
on this controlled corpus and two hosted deployments, preservation calibration
separates two defense goals that earlier gates conflated:

1. Preserve abstention when trusted current evidence is genuinely insufficient.
2. Preserve useful yes/no answers when trusted current evidence directly
   supports or refutes the proposition.

The paired analysis shows the gains are concentrated on direct controls rather
than evidence gaps: A10 leaves all paired insufficient-evidence rows correctly
abstained and repairs false abstentions on direct yes/no controls.

## Public Artifact Packet

The public packet is designed to be reviewable without access to the private
hosted run directories:

| Artifact | Purpose |
| --- | --- |
| `artifacts/long-graph-v2/README.md` | Data package schema, redactions, and rebuild path. |
| `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl` | Sanitized primary hosted rows. |
| `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl` | Sanitized cross-model replication rows. |
| `artifacts/long-graph-v2/blind-audit-queue.jsonl` | Blinded evidence-review queue for all 576 public rows. |
| `docs/paired-long-graph-v2-preservation-analysis.md` | Deployment-aware paired tests and effect sizes. |
| `docs/long-graph-v2-preservation-casebook.md` | Row-level repair cases with trusted/current evidence pages. |
| `docs/long-graph-v2-preservation-transition-analysis.md` | Relation-label transition analysis for repaired rows. |
| `docs/long-graph-v2-public-artifact-validation.md` | Machine checks for row counts, redaction, summaries, and IDs. |
| `docs/blind-audit-validation.md` | Machine checks for blind queue/key alignment and leakage control. |
| `docs/research-artifact-manifest.md` | SHA-256 checksums and claim map. |

## Limitations

The corpus is synthetic and intentionally controlled. The results should be
read as a mechanism study of evidence handling under agentic web poisoning, not
as a deployment claim for arbitrary real websites, arbitrary tools, or
production policy settings. The strongest next test is to vary the corpus
generator, add distractors with subtler provenance cues, and replicate the same
paired design across more model families and search/reranking stacks.
