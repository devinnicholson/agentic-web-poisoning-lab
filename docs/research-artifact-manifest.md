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
| Repository README | `README.md` | markdown | 545 lines | 23312 | `c0cbc34280a670dee799cf2ee6d090ad3f42240e8ada2054bb03cb5d63ccdecb` |
| Long-graph v2 tasks | `data/tasks.graph-long-v2.jsonl` | jsonl | 24 records | 13229 | `cb39b495f6aee1e3960d6870238a7f679f3ff6de487c2a858d7df8960c5b864a` |
| Long-graph v2 pages | `data/pages.graph-long-v2.jsonl` | jsonl | 128 records | 60366 | `afb3a01edc456578f52f44ae76cf831559a298f12ec147d3298154e0230fa965` |
| Long-graph v2 public artifact README | `artifacts/long-graph-v2/README.md` | markdown | 65 lines | 3087 | `75e1eca1b111f84c6b8e35c53baa9ba6f95fbdafa720ea05fdca799cd350d17e` |
| Primary hosted long-graph v2 rows | `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl` | jsonl | 360 records | 1911879 | `4298dc4612e4f24a809d262f18e6e9a8436ee52ac0f54f903dafa557185d468c` |
| Cross-model hosted long-graph v2 rows | `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl` | jsonl | 216 records | 1401699 | `1a6ee8393d3927f1ffde52d71af47cf3928334dbc1ac108fac4a77d6bf4e26bf` |
| Primary hosted long-graph v2 summary | `artifacts/long-graph-v2/hosted-gpt5-mini-summary.json` | json | 82 lines | 2241 | `1cb27b9b052dd3ee3b7336e5deb9f80bda42604fb47b945a7b7638865221e8b0` |
| Cross-model hosted long-graph v2 summary | `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-summary.json` | json | 50 lines | 1355 | `8a48fd19ec49919cb3ba5ed1c115608bd9ec6132b5ba21db156a32b989c555f9` |
| Blinded long-graph v2 audit queue | `artifacts/long-graph-v2/blind-audit-queue.jsonl` | jsonl | 576 records | 1998859 | `b5364a1ebf1cba91714341766dde3e6d4d0a291b7af800e4130a68ba31c4cd30` |
| Long-graph v2 audit unblinding key | `artifacts/long-graph-v2/blind-audit-key.jsonl` | jsonl | 576 records | 794574 | `1e8487e12e6e1cfb90d008692365734ef1013550f0d8602cf44389ef635e4469` |
| Long-graph v2 corpus card | `docs/long-graph-v2-corpus-card.md` | markdown | 82 lines | 4062 | `bc6ed9f3599385581a99e0ca5890e37f5ade3e30b6860bce7823764ae1a3a928` |
| Long-graph v2 benchmark specification | `docs/benchmark-spec.md` | markdown | 244 lines | 10455 | `50f7fae443ddcfeadfc4e523efba1f2e68009dd7ff5ca3bc698294192726c561` |
| Extended abstract | `docs/extended-abstract.md` | markdown | 75 lines | 4422 | `72fda4105904da6c5ab8abfdfbd7298ae5a69cecbfa0001880503d3a2416f5b2` |
| Demo script | `docs/demo-script.md` | markdown | 113 lines | 4468 | `37a88d304f12cde845844c2c7fecb5eb4cfa3ac2d3a06d03ce2f0eb3cf6c9194` |
| Threat model and safety scope | `docs/threat-model.md` | markdown | 100 lines | 3849 | `5ddbea092e915d1b2fcc882de4c96d5ac7de93a60cb8e3037dfd2cc80a7bb746` |
| Submission checklist | `docs/submission-checklist.md` | markdown | 103 lines | 3303 | `f5f53bba6ee8127eb83d35bd948603d53713c1c8802c47770e48897a8696bc5f` |
| Blind manual audit protocol | `docs/manual-audit-protocol.md` | markdown | 358 lines | 15971 | `ccdfa2aec7a85e0b960956e09dc6ac774bc5f92f96ad9ada953db908d6001a04` |
| Blind audit validation report | `docs/blind-audit-validation.md` | markdown | 40 lines | 1638 | `cbae25b9187a66cbd505971887f20f94cb361dda8b51732580a4e6397f6c4d28` |
| Held-out v3 replication preregistration | `docs/v3-replication-plan.md` | markdown | 309 lines | 13732 | `9e940f4d2fa81267c7f9fbca3fb934e22d46dfe3b6e3ff6e19789c54701e8ac4` |
| v0.1 release notes | `docs/release-notes-v0.1-long-graph-v2.md` | markdown | 60 lines | 2463 | `389613ce0bfd8b75909077056a8e089e41a4bb2a7fc1bb545a6d809cea37e4ce` |
| Paired preservation appendix | `docs/paired-long-graph-v2-preservation-analysis.md` | markdown | 95 lines | 10314 | `c5508974ec2b7c66e518c5bfd9464796d54e83a0da1904faac90fc80c1754df9` |
| Preservation repair casebook | `docs/long-graph-v2-preservation-casebook.md` | markdown | 358 lines | 39041 | `c324b3c9f0e415d23f5a1c03b2d2e409e60fca3caedfe1f4812992e093a554f8` |
| Preservation transition appendix | `docs/long-graph-v2-preservation-transition-analysis.md` | markdown | 62 lines | 4267 | `50c2856d6f6102ae9196387deba775b7d1f4e9fa509bb60111c2d1f3cb598746` |
| Public artifact validation report | `docs/long-graph-v2-public-artifact-validation.md` | markdown | 44 lines | 1932 | `819f350f584ac8cbd3092721463977ba77a8b4aae4e238617d8d7cc110e59344` |
| Primary hosted long-graph v2 narrative | `docs/hosted-long-graph-v2-summary.md` | markdown | 122 lines | 5327 | `e6476a083a54b23e8b642b0fd17137c23e769611814a76f43e5087387298aede` |
| Cross-model hosted long-graph v2 narrative | `docs/hosted-long-graph-v2-cross-model-summary.md` | markdown | 87 lines | 3699 | `155a28d607f6df7f62185f0f3b2f70f9af50ff80d1410782e3a6c2cef385abee` |
| Research dashboard | `static/research-dashboard.html` | html | 1653 lines | 61675 | `bf747544da343e6804bd51290220c0dfba8487b1fdfd2b9dce9a5b7ffe7a37e1` |
| Reviewer guide | `docs/reviewer-guide.md` | markdown | 92 lines | 3986 | `f18aa732123742e051890e91176c07b7a0c0e44bf5cd6214162db2d8e67414f2` |

## Claim Map

| Claim | Primary artifacts |
| --- | --- |
| Corpus design is balanced and page-budget controlled | `docs/benchmark-spec.md`, `docs/long-graph-v2-corpus-card.md`, `data/tasks.graph-long-v2.jsonl`, `data/pages.graph-long-v2.jsonl` |
| A10 repairs direct-control over-abstention across two deployments | `README.md`, `docs/extended-abstract.md`, `docs/paired-long-graph-v2-preservation-analysis.md`, `docs/hosted-long-graph-v2-summary.md`, `docs/hosted-long-graph-v2-cross-model-summary.md` |
| Row-level repairs are inspectable against trusted/current pages | `docs/long-graph-v2-preservation-casebook.md`, `data/pages.graph-long-v2.jsonl` |
| Page-label changes are concentrated on repaired rows | `docs/long-graph-v2-preservation-transition-analysis.md`, `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl`, `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl` |
| Public dashboard summarizes the committed aggregate results | `static/research-dashboard.html` |
| Public snapshot integrity is machine-checkable | `artifacts/long-graph-v2/README.md`, `docs/long-graph-v2-public-artifact-validation.md`, `docs/research-artifact-manifest.md` |
| Blind review and held-out replication are preregistered | `docs/manual-audit-protocol.md`, `artifacts/long-graph-v2/blind-audit-queue.jsonl`, `artifacts/long-graph-v2/blind-audit-key.jsonl`, `docs/blind-audit-validation.md`, `docs/v3-replication-plan.md` |
| Reviewer path and safety scope are documented | `docs/reviewer-guide.md`, `docs/demo-script.md`, `docs/threat-model.md`, `docs/submission-checklist.md`, `docs/release-notes-v0.1-long-graph-v2.md` |
