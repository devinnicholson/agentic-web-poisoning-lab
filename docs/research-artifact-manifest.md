# Research Artifact Manifest

This deterministic manifest records the key public artifacts for the long-graph v2 preservation finding. It avoids timestamps so it can be regenerated and diffed cleanly.

## Regeneration Commands

```bash
make long-graph-v2-corpus-card-refresh
make public-snapshot-long-graph-v2
make blind-audit-long-graph-v2-public
make validate-blind-audit-long-graph-v2
make paired-analysis-long-graph-v2-preservation
make casebook-long-graph-v2-preservation
make transition-analysis-long-graph-v2-preservation
make validate-long-graph-v2-public-artifacts
make artifact-manifest-refresh
```

## Artifact Checksums

| Artifact | Path | Kind | Records/lines | Bytes | SHA-256 |
| --- | --- | --- | ---: | ---: | --- |
| Citation metadata | `CITATION.cff` | yaml | 21 lines | 739 | `26a772991fb896c0098efaa1db5993df8d7618389ba4c57cd8d4579bb4b0d729` |
| Repository README | `README.md` | markdown | 547 lines | 23473 | `90ce5afd7b9e0308e993392641e4947d592707b102b7195fb5e6e0fdbc93efbb` |
| Long-graph v2 tasks | `data/tasks.graph-long-v2.jsonl` | jsonl | 24 records | 13229 | `cb39b495f6aee1e3960d6870238a7f679f3ff6de487c2a858d7df8960c5b864a` |
| Long-graph v2 pages | `data/pages.graph-long-v2.jsonl` | jsonl | 128 records | 60366 | `afb3a01edc456578f52f44ae76cf831559a298f12ec147d3298154e0230fa965` |
| Long-graph v2 public artifact README | `artifacts/long-graph-v2/README.md` | markdown | 66 lines | 3152 | `e360afc605b08809526ef2fd0044a2dfb1aa962bf4643a5a0e63aba5166d3cf9` |
| Primary hosted long-graph v2 rows | `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl` | jsonl | 360 records | 1911879 | `4298dc4612e4f24a809d262f18e6e9a8436ee52ac0f54f903dafa557185d468c` |
| Cross-model hosted long-graph v2 rows | `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl` | jsonl | 216 records | 1401699 | `1a6ee8393d3927f1ffde52d71af47cf3928334dbc1ac108fac4a77d6bf4e26bf` |
| Primary hosted long-graph v2 summary | `artifacts/long-graph-v2/hosted-gpt5-mini-summary.json` | json | 82 lines | 2241 | `1cb27b9b052dd3ee3b7336e5deb9f80bda42604fb47b945a7b7638865221e8b0` |
| Cross-model hosted long-graph v2 summary | `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-summary.json` | json | 50 lines | 1355 | `8a48fd19ec49919cb3ba5ed1c115608bd9ec6132b5ba21db156a32b989c555f9` |
| Blinded long-graph v2 audit queue | `artifacts/long-graph-v2/blind-audit-queue.jsonl` | jsonl | 576 records | 1998859 | `b5364a1ebf1cba91714341766dde3e6d4d0a291b7af800e4130a68ba31c4cd30` |
| Long-graph v2 audit unblinding key | `artifacts/long-graph-v2/blind-audit-key.jsonl` | jsonl | 576 records | 794574 | `1e8487e12e6e1cfb90d008692365734ef1013550f0d8602cf44389ef635e4469` |
| Long-graph v2 corpus card | `docs/long-graph-v2-corpus-card.md` | markdown | 82 lines | 4062 | `bc6ed9f3599385581a99e0ca5890e37f5ade3e30b6860bce7823764ae1a3a928` |
| Long-graph v2 benchmark specification | `docs/benchmark-spec.md` | markdown | 244 lines | 10455 | `50f7fae443ddcfeadfc4e523efba1f2e68009dd7ff5ca3bc698294192726c561` |
| Extended abstract | `docs/extended-abstract.md` | markdown | 76 lines | 4525 | `b3402e6129f12203107deb48094b68daec49adaac5ef5bc94b51ea57974db82a` |
| Demo script | `docs/demo-script.md` | markdown | 114 lines | 4600 | `cffe8737934529d2c7e1f71f832baef0e49b7dea5cb6945b28ee60389cb9b973` |
| Threat model and safety scope | `docs/threat-model.md` | markdown | 100 lines | 3849 | `5ddbea092e915d1b2fcc882de4c96d5ac7de93a60cb8e3037dfd2cc80a7bb746` |
| Submission checklist | `docs/submission-checklist.md` | markdown | 105 lines | 3415 | `248a54eb698354344c7358db20098d32940f18916017586ce57482ea9d590897` |
| Blind manual audit protocol | `docs/manual-audit-protocol.md` | markdown | 362 lines | 16139 | `3047088042d83cfe14bdfbf7b8f5fcc7285590293cf05eaa56fa0b7c80119806` |
| Blind audit validation report | `docs/blind-audit-validation.md` | markdown | 40 lines | 1638 | `cbae25b9187a66cbd505971887f20f94cb361dda8b51732580a4e6397f6c4d28` |
| Blind audit label schema | `docs/blind-audit-label-schema.md` | markdown | 64 lines | 3088 | `d09f438efbe8a23a5a04031b37613b1576291e42a5e1146f9f03d33d9cd1cf8e` |
| Held-out v3 replication preregistration | `docs/v3-replication-plan.md` | markdown | 309 lines | 13732 | `9e940f4d2fa81267c7f9fbca3fb934e22d46dfe3b6e3ff6e19789c54701e8ac4` |
| v0.1 release notes | `docs/release-notes-v0.1-long-graph-v2.md` | markdown | 60 lines | 2463 | `389613ce0bfd8b75909077056a8e089e41a4bb2a7fc1bb545a6d809cea37e4ce` |
| Paired preservation appendix | `docs/paired-long-graph-v2-preservation-analysis.md` | markdown | 95 lines | 10314 | `c5508974ec2b7c66e518c5bfd9464796d54e83a0da1904faac90fc80c1754df9` |
| Preservation repair casebook | `docs/long-graph-v2-preservation-casebook.md` | markdown | 358 lines | 39041 | `c324b3c9f0e415d23f5a1c03b2d2e409e60fca3caedfe1f4812992e093a554f8` |
| Preservation transition appendix | `docs/long-graph-v2-preservation-transition-analysis.md` | markdown | 62 lines | 4267 | `50c2856d6f6102ae9196387deba775b7d1f4e9fa509bb60111c2d1f3cb598746` |
| Public artifact validation report | `docs/long-graph-v2-public-artifact-validation.md` | markdown | 44 lines | 1932 | `819f350f584ac8cbd3092721463977ba77a8b4aae4e238617d8d7cc110e59344` |
| Primary hosted long-graph v2 narrative | `docs/hosted-long-graph-v2-summary.md` | markdown | 122 lines | 5327 | `e6476a083a54b23e8b642b0fd17137c23e769611814a76f43e5087387298aede` |
| Cross-model hosted long-graph v2 narrative | `docs/hosted-long-graph-v2-cross-model-summary.md` | markdown | 87 lines | 3699 | `155a28d607f6df7f62185f0f3b2f70f9af50ff80d1410782e3a6c2cef385abee` |
| Research dashboard | `static/research-dashboard.html` | html | 1657 lines | 61915 | `dfb0a760a8aca1be40b238c1a8df74d4a567b32ad4995529a951dcea03a5c5d5` |
| Reviewer guide | `docs/reviewer-guide.md` | markdown | 96 lines | 4204 | `10a4b397b63f2f20f6ad9cead0f86a7756e6fb37ccc37b6ecfb85d458c098183` |

## Claim Map

| Claim | Primary artifacts |
| --- | --- |
| Corpus design is balanced and page-budget controlled | `docs/benchmark-spec.md`, `docs/long-graph-v2-corpus-card.md`, `data/tasks.graph-long-v2.jsonl`, `data/pages.graph-long-v2.jsonl` |
| A10 repairs direct-control over-abstention across two deployments | `README.md`, `docs/extended-abstract.md`, `docs/paired-long-graph-v2-preservation-analysis.md`, `docs/hosted-long-graph-v2-summary.md`, `docs/hosted-long-graph-v2-cross-model-summary.md` |
| Row-level repairs are inspectable against trusted/current pages | `docs/long-graph-v2-preservation-casebook.md`, `data/pages.graph-long-v2.jsonl` |
| Page-label changes are concentrated on repaired rows | `docs/long-graph-v2-preservation-transition-analysis.md`, `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl`, `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl` |
| Public dashboard summarizes the committed aggregate results | `static/research-dashboard.html` |
| Public snapshot integrity is machine-checkable | `artifacts/long-graph-v2/README.md`, `docs/long-graph-v2-public-artifact-validation.md`, `docs/research-artifact-manifest.md` |
| Blind review and held-out replication are preregistered | `docs/manual-audit-protocol.md`, `artifacts/long-graph-v2/blind-audit-queue.jsonl`, `artifacts/long-graph-v2/blind-audit-key.jsonl`, `docs/blind-audit-validation.md`, `docs/blind-audit-label-schema.md`, `docs/v3-replication-plan.md` |
| Reviewer path and safety scope are documented | `docs/reviewer-guide.md`, `docs/demo-script.md`, `docs/threat-model.md`, `docs/submission-checklist.md`, `docs/release-notes-v0.1-long-graph-v2.md` |
