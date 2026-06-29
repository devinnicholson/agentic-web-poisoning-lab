# Research Artifact Manifest

This deterministic manifest records the key public artifacts for the long-graph v2 preservation finding. It avoids timestamps so it can be regenerated and diffed cleanly.

## Regeneration Commands

```bash
make long-graph-v2-corpus-card-refresh
make paired-analysis-long-graph-v2-preservation
make casebook-long-graph-v2-preservation
make transition-analysis-long-graph-v2-preservation
make artifact-manifest-refresh
```

## Artifact Checksums

| Artifact | Path | Kind | Records/lines | Bytes | SHA-256 |
| --- | --- | --- | ---: | ---: | --- |
| Long-graph v2 tasks | `data/tasks.graph-long-v2.jsonl` | jsonl | 24 records | 13229 | `cb39b495f6aee1e3960d6870238a7f679f3ff6de487c2a858d7df8960c5b864a` |
| Long-graph v2 pages | `data/pages.graph-long-v2.jsonl` | jsonl | 128 records | 60366 | `afb3a01edc456578f52f44ae76cf831559a298f12ec147d3298154e0230fa965` |
| Primary hosted long-graph v2 rows | `experiments/results/hosted-long-graph-v2-pilot/results.jsonl` | jsonl | 360 records | 1863999 | `0652c219fffd23a9d5fcf0cd835cd0b40873257b7ee30f5406d12faf3efdb7bf` |
| Cross-model hosted long-graph v2 rows | `experiments/results/hosted-long-graph-v2-gpt41mini-a8-a10-repeats/results.jsonl` | jsonl | 216 records | 1375347 | `0bc6b8fba316cc3b4b48291f6af0a13f9a6b7f31bb9a1d9f5124a87987144e63` |
| Primary hosted long-graph v2 summary | `experiments/results/hosted-long-graph-v2-pilot/summary.json` | json | 82 lines | 2241 | `1cb27b9b052dd3ee3b7336e5deb9f80bda42604fb47b945a7b7638865221e8b0` |
| Cross-model hosted long-graph v2 summary | `experiments/results/hosted-long-graph-v2-gpt41mini-a8-a10-repeats/summary.json` | json | 50 lines | 1355 | `8a48fd19ec49919cb3ba5ed1c115608bd9ec6132b5ba21db156a32b989c555f9` |
| Long-graph v2 corpus card | `docs/long-graph-v2-corpus-card.md` | markdown | 82 lines | 4062 | `bc6ed9f3599385581a99e0ca5890e37f5ade3e30b6860bce7823764ae1a3a928` |
| Paired preservation appendix | `docs/paired-long-graph-v2-preservation-analysis.md` | markdown | 95 lines | 10337 | `162ccfce5160aaf303ba5f05461bec341c5ba7a5c2bd1600142e7887e67c1964` |
| Preservation repair casebook | `docs/long-graph-v2-preservation-casebook.md` | markdown | 358 lines | 39064 | `0b098bfe970203781b2ab1804cb09172249575a9008c4e37c8500a90feefa4a0` |
| Preservation transition appendix | `docs/long-graph-v2-preservation-transition-analysis.md` | markdown | 62 lines | 4290 | `c91725035114e157b4357ca867f89e6862ec642f6df64b9abf6b43b028bef05d` |
| Primary hosted long-graph v2 narrative | `docs/hosted-long-graph-v2-summary.md` | markdown | 121 lines | 5294 | `f5241b9da032963767762b0de7693b95aa9610a2efcc9aa652b62829f4c5d28e` |
| Cross-model hosted long-graph v2 narrative | `docs/hosted-long-graph-v2-cross-model-summary.md` | markdown | 86 lines | 3658 | `fe974dd10a218eda0b03d457dd2de593341d55c5f3d9854a5f911bf5180b5608` |
| Research dashboard | `static/research-dashboard.html` | html | 1588 lines | 57895 | `efc68d74f5ffea6776cb62c8aeecb70b852637b8c814a88b96abe0fa697d441f` |

## Claim Map

| Claim | Primary artifacts |
| --- | --- |
| Corpus design is balanced and page-budget controlled | `docs/long-graph-v2-corpus-card.md`, `data/tasks.graph-long-v2.jsonl`, `data/pages.graph-long-v2.jsonl` |
| A10 repairs direct-control over-abstention across two deployments | `docs/paired-long-graph-v2-preservation-analysis.md`, `docs/hosted-long-graph-v2-summary.md`, `docs/hosted-long-graph-v2-cross-model-summary.md` |
| Row-level repairs are inspectable against trusted/current pages | `docs/long-graph-v2-preservation-casebook.md`, `data/pages.graph-long-v2.jsonl` |
| Page-label changes are concentrated on repaired rows | `docs/long-graph-v2-preservation-transition-analysis.md`, `experiments/results/hosted-long-graph-v2-pilot/results.jsonl`, `experiments/results/hosted-long-graph-v2-gpt41mini-a8-a10-repeats/results.jsonl` |
| Public dashboard summarizes the committed aggregate results | `static/research-dashboard.html` |
