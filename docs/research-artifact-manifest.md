# Research Artifact Manifest

This deterministic manifest records the key public artifacts for the long-graph v2 preservation finding. It avoids timestamps so it can be regenerated and diffed cleanly.

## Regeneration Commands

```bash
make long-graph-v2-corpus-card-refresh
make public-snapshot-long-graph-v2
make paired-analysis-long-graph-v2-preservation
make casebook-long-graph-v2-preservation
make transition-analysis-long-graph-v2-preservation
make validate-long-graph-v2-public-artifacts
make artifact-manifest-refresh
```

## Artifact Checksums

| Artifact | Path | Kind | Records/lines | Bytes | SHA-256 |
| --- | --- | --- | ---: | ---: | --- |
| Long-graph v2 tasks | `data/tasks.graph-long-v2.jsonl` | jsonl | 24 records | 13229 | `cb39b495f6aee1e3960d6870238a7f679f3ff6de487c2a858d7df8960c5b864a` |
| Long-graph v2 pages | `data/pages.graph-long-v2.jsonl` | jsonl | 128 records | 60366 | `afb3a01edc456578f52f44ae76cf831559a298f12ec147d3298154e0230fa965` |
| Primary hosted long-graph v2 rows | `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl` | jsonl | 360 records | 1911879 | `4298dc4612e4f24a809d262f18e6e9a8436ee52ac0f54f903dafa557185d468c` |
| Cross-model hosted long-graph v2 rows | `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl` | jsonl | 216 records | 1401699 | `1a6ee8393d3927f1ffde52d71af47cf3928334dbc1ac108fac4a77d6bf4e26bf` |
| Primary hosted long-graph v2 summary | `artifacts/long-graph-v2/hosted-gpt5-mini-summary.json` | json | 82 lines | 2241 | `1cb27b9b052dd3ee3b7336e5deb9f80bda42604fb47b945a7b7638865221e8b0` |
| Cross-model hosted long-graph v2 summary | `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-summary.json` | json | 50 lines | 1355 | `8a48fd19ec49919cb3ba5ed1c115608bd9ec6132b5ba21db156a32b989c555f9` |
| Long-graph v2 corpus card | `docs/long-graph-v2-corpus-card.md` | markdown | 82 lines | 4062 | `bc6ed9f3599385581a99e0ca5890e37f5ade3e30b6860bce7823764ae1a3a928` |
| Paired preservation appendix | `docs/paired-long-graph-v2-preservation-analysis.md` | markdown | 95 lines | 10314 | `c5508974ec2b7c66e518c5bfd9464796d54e83a0da1904faac90fc80c1754df9` |
| Preservation repair casebook | `docs/long-graph-v2-preservation-casebook.md` | markdown | 358 lines | 39041 | `c324b3c9f0e415d23f5a1c03b2d2e409e60fca3caedfe1f4812992e093a554f8` |
| Preservation transition appendix | `docs/long-graph-v2-preservation-transition-analysis.md` | markdown | 62 lines | 4267 | `50c2856d6f6102ae9196387deba775b7d1f4e9fa509bb60111c2d1f3cb598746` |
| Public artifact validation report | `docs/long-graph-v2-public-artifact-validation.md` | markdown | 44 lines | 1932 | `819f350f584ac8cbd3092721463977ba77a8b4aae4e238617d8d7cc110e59344` |
| Primary hosted long-graph v2 narrative | `docs/hosted-long-graph-v2-summary.md` | markdown | 122 lines | 5327 | `e6476a083a54b23e8b642b0fd17137c23e769611814a76f43e5087387298aede` |
| Cross-model hosted long-graph v2 narrative | `docs/hosted-long-graph-v2-cross-model-summary.md` | markdown | 87 lines | 3699 | `155a28d607f6df7f62185f0f3b2f70f9af50ff80d1410782e3a6c2cef385abee` |
| Research dashboard | `static/research-dashboard.html` | html | 1604 lines | 58826 | `5401901e1e352193eefb7cae372e11ef6d7e4eefc3f53ee34ddc977ee5611489` |
| Reviewer guide | `docs/reviewer-guide.md` | markdown | 82 lines | 3387 | `c66f298bebbf96107421d67d1bd2c585be1f3d2e91553fab49021dc5a79270d3` |

## Claim Map

| Claim | Primary artifacts |
| --- | --- |
| Corpus design is balanced and page-budget controlled | `docs/long-graph-v2-corpus-card.md`, `data/tasks.graph-long-v2.jsonl`, `data/pages.graph-long-v2.jsonl` |
| A10 repairs direct-control over-abstention across two deployments | `docs/paired-long-graph-v2-preservation-analysis.md`, `docs/hosted-long-graph-v2-summary.md`, `docs/hosted-long-graph-v2-cross-model-summary.md` |
| Row-level repairs are inspectable against trusted/current pages | `docs/long-graph-v2-preservation-casebook.md`, `data/pages.graph-long-v2.jsonl` |
| Page-label changes are concentrated on repaired rows | `docs/long-graph-v2-preservation-transition-analysis.md`, `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl`, `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl` |
| Public dashboard summarizes the committed aggregate results | `static/research-dashboard.html` |
| Public snapshot integrity is machine-checkable | `docs/long-graph-v2-public-artifact-validation.md`, `docs/research-artifact-manifest.md` |
| Reviewer path and safety scope are documented | `docs/reviewer-guide.md` |
