# Submission Checklist

Use this checklist before sharing the project as a class artifact, poster,
workshop submission, or research demo.

## Claim

- [x] Main claim is narrow and falsifiable.
- [x] Claim is tied to the long-graph v2 synthetic corpus, not all real-world
      agents.
- [x] Primary effect is stated as paired direct-control repair rather than
      generic robustness.
- [x] Evidence-gap abstention preservation is reported separately from direct
      yes/no answer preservation.

Primary references:

- `docs/extended-abstract.md`
- `docs/paired-long-graph-v2-preservation-analysis.md`
- `docs/hosted-long-graph-v2-summary.md`
- `docs/hosted-long-graph-v2-cross-model-summary.md`

## Data and Artifacts

- [x] Public row snapshots are committed under `artifacts/long-graph-v2/`.
- [x] Public rows are sanitized for provider-only identifiers.
- [x] Public row schema and redactions are documented.
- [x] Artifact checksums are recorded.
- [x] Blinded manual-audit queue and unblinding key are generated from the
      public row snapshots.
- [x] Machine validation checks row counts, summary consistency, redaction,
      condition coverage, and task/page references.

Primary references:

- `artifacts/long-graph-v2/README.md`
- `artifacts/long-graph-v2/blind-audit-queue.jsonl`
- `docs/long-graph-v2-public-artifact-validation.md`
- `docs/research-artifact-manifest.md`

## Method

- [x] Corpus balance is documented: 24 tasks, 8 domains, 4 trusted pages and 4
      adversarial pages per task.
- [x] Defense conditions are compared on the same task/repeat cells.
- [x] Cross-model replication is included.
- [x] Row-level qualitative cases are available for inspection.
- [x] Benchmark schema, model-adapter contract, and metrics are specified.
- [x] Held-out v3 replication criteria are preregistered before v3 collection.

Primary references:

- `docs/benchmark-spec.md`
- `docs/long-graph-v2-corpus-card.md`
- `docs/long-graph-v2-preservation-casebook.md`
- `docs/long-graph-v2-preservation-transition-analysis.md`
- `docs/v3-replication-plan.md`

## Reproducibility

- [x] Generated artifacts have freshness tests in CI.
- [x] Public snapshots can be regenerated from private hosted output
      directories.
- [x] CI passes on Python 3.11 and 3.12.
- [x] Citation metadata is present.
- [x] Blind audit generation is covered by tests.

Primary references:

- `tests/test_blind_audit.py`
- `tests/test_generated_research_artifacts.py`
- `.github/workflows/ci.yml`
- `CITATION.cff`
- `docs/reproducibility.md`

## Demo

- [x] Dashboard summarizes the result.
- [x] Demo script gives exact talk track and caveats.
- [x] Reviewer guide provides 5-, 15-, and 45-minute paths.
- [x] Safety scope is included in the demo flow.

Primary references:

- `static/research-dashboard.html`
- `docs/demo-script.md`
- `docs/reviewer-guide.md`
- `docs/threat-model.md`

## Safety and Limitations

- [x] Synthetic-data boundary is explicit.
- [x] Real-world abuse paths are out of scope.
- [x] Limitations and future work are documented.
- [x] The repo does not claim production robustness.

Primary references:

- `docs/threat-model.md`
- `docs/extended-abstract.md`
