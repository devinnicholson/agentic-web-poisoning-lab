# v0.1 Long-Graph v2 Artifact Release Notes

This release packages the long-graph v2 preservation finding as a public,
reviewable AI safety artifact.

## Headline

The A10 preservation-calibrated relation gate preserved evidence-gap abstention
while repairing direct-control over-abstention on a synthetic agentic
web-poisoning benchmark.

Across two hosted Azure OpenAI deployments:

| Metric | Result |
| --- | --- |
| Public hosted rows | 576 sanitized rows |
| Primary A10 accuracy | 72/72 |
| Cross-model A10 accuracy | 72/72 |
| Primary A10 direct controls | 48/48 |
| Cross-model A10 direct controls | 48/48 |
| A10 attack successes | 0/72 on each deployment |
| A10 poisoned citations | 0/72 on each deployment |
| A8 to A10 paired repair | 14 direct-control rows fixed, 0 new direct-control misses |
| A9 to A10 paired repair | 19 direct-control rows fixed, 0 new direct-control misses |

## Included Public Artifacts

- `README.md`: portfolio front door and fast review map.
- `docs/extended-abstract.md`: paper-style overview.
- `static/research-dashboard.html`: self-contained dashboard.
- `artifacts/long-graph-v2/`: sanitized public row snapshots and package README.
- `docs/paired-long-graph-v2-preservation-analysis.md`: paired tests and effect sizes.
- `docs/long-graph-v2-preservation-casebook.md`: row-level repair examples.
- `docs/long-graph-v2-preservation-transition-analysis.md`: relation-label transition analysis.
- `docs/long-graph-v2-public-artifact-validation.md`: public artifact integrity checks.
- `docs/threat-model.md`: safety scope and release boundary.
- `docs/demo-script.md`: 5- to 7-minute talk track.
- `docs/submission-checklist.md`: class/workshop readiness checklist.
- `docs/research-artifact-manifest.md`: row counts, byte counts, and SHA-256 hashes.
- `CITATION.cff`: citation metadata.

## Validation Status

At release preparation time:

- Local `make test`: 90 tests passing.
- Static dashboard HTML parses successfully.
- `git diff --check` passes.
- GitHub Actions passes on Python 3.11 and Python 3.12 for `main`.

## Scope

This release is a controlled synthetic benchmark and public artifact packet. It
does not claim production robustness for arbitrary agents, arbitrary websites,
or arbitrary retrieval stacks. The intended use is defensive evaluation,
mechanism inspection, and follow-on replication.

## Suggested Citation

Use `CITATION.cff` or cite the repository URL with the `v0.1-long-graph-v2` tag.
