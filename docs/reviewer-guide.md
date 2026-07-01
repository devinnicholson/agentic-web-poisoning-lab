# Reviewer Guide

This guide is for a reviewer who wants to inspect the long-graph v2
preservation result without reading the whole repository.

## Five-Minute Path

1. Read `docs/extended-abstract.md`.
2. Open `static/research-dashboard.html`.
3. In the Graph Stress view, read the v2 tables and the v2 public artifacts
   packet.
4. Open `docs/research-artifact-manifest.md` and confirm the row counts:
   360 primary hosted rows, 216 cross-model hosted rows, 24 tasks, and 128
   pages.
5. Open `docs/blind-audit-validation.md` and confirm the 576-row blinded
   queue/key packet passes leakage and alignment checks.
6. Open `docs/blind-audit-label-schema.md` to see how independent reviewer
   labels would be validated before analysis.

Expected takeaway: A10 reaches 72/72 accuracy on both deployments, while A8
and A9 preserve evidence-gap abstention but over-abstain on direct controls.

## Fifteen-Minute Path

1. Read `docs/long-graph-v2-corpus-card.md` to verify the balanced corpus
   design: 8 yes, 8 no, and 8 insufficient-evidence tasks across 8 domains,
   with 4 required pages and 4 attack pages per task.
2. Read `docs/paired-long-graph-v2-preservation-analysis.md` for the paired
   McNemar tests:
   - A10 fixes 14 direct-control rows relative to A8 with 0 new direct-control
     misses.
   - A10 fixes 19 direct-control rows relative to A9 with 0 new direct-control
     misses.
   - A8, A9, and A10 all preserve 48/48 paired evidence-gap abstentions.
3. Read `docs/long-graph-v2-preservation-transition-analysis.md` to check the
   mechanism claim: 35 page-label transition observations occur on 33 repaired
   direct-control rows, while 0 non-repaired direct-control rows changed
   labels.

Expected takeaway: the improvement is not a broad relaxation of abstention; it
is concentrated on preserving direct support and direct refutation where trusted
current pages answer the question.

## Forty-Five-Minute Path

1. Read `docs/long-graph-v2-preservation-casebook.md`.
2. For each representative case, compare:
   - the A8/A9 answer and relation labels,
   - the paired A10 answer and relation labels,
   - the trusted/current evidence pages cited by A10,
   - the safety metrics showing no poisoned citations or attack success.
3. Spot-check raw rows in:
   - `artifacts/long-graph-v2/hosted-gpt5-mini-results.jsonl`,
   - `artifacts/long-graph-v2/hosted-gpt41-mini-a8-a10-results.jsonl`.
4. Rebuild the derived artifacts:

```bash
make public-snapshot-long-graph-v2
make long-graph-v2-corpus-card-refresh
make paired-analysis-long-graph-v2-preservation
make casebook-long-graph-v2-preservation
make transition-analysis-long-graph-v2-preservation
make validate-long-graph-v2-public-artifacts
make validate-blind-audit-long-graph-v2
make artifact-manifest-refresh
```

Expected takeaway: the corpus, aggregate statistics, row-level repairs,
mechanism analysis, validation report, and checksum manifest can all be
regenerated from committed files.

## Falsification Checks

The result would be weakened if any of the following are found:

- A10 direct-control gains come with evidence-gap regressions.
- A10 repairs rely on poisoned, stale, or low-trust citations.
- Label changes appear broadly on already-correct rows rather than on repaired
  rows.
- The cross-model deployment fails to reproduce the A10 direct-control repair.
- The generated artifacts cannot be reproduced from the committed JSONL files.
- The validation report misses unredacted provider identifiers or unresolved
  task/page references.
- The blinded audit validation report finds raw task/page IDs, condition names,
  metric labels, provider metadata, non-null reviewer labels, or queue/key
  alignment failures.
- Submitted blind-audit labels cannot be validated against
  `docs/blind-audit-label-schema.md`.

## Safety Scope

The corpus is synthetic and uses synthetic local URLs. The project does not
publish live exploit instructions for poisoning real websites or services. The
research focus is defensive evaluation of agent evidence handling under
controlled web-poisoning pressure. `docs/threat-model.md` gives the full
adversary model, release boundary, out-of-scope misuse, and remaining risk.
