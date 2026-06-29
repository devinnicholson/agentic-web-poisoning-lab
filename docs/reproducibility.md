# Reproducibility Notes

This repo keeps raw generated result files out of Git, but every committed
snapshot can be regenerated from the public synthetic corpus and harness code.

## Local Benchmarks

Run the deterministic seed benchmark:

```bash
make research-refresh
```

Run the deterministic challenge benchmark with A5:

```bash
make strict-challenge-refresh
```

Local outputs are written under `experiments/results/`.

## Hosted Benchmarks

Hosted runs require `.env` settings for an Azure OpenAI chat-completions
deployment:

```text
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=...
```

Run the full hosted matrix:

```bash
make hosted-full-refresh
```

Run the A1-A4 challenge matrix:

```bash
make hosted-challenge-refresh
```

Run the A1-A5 strict-abstention challenge matrix:

```bash
make hosted-strict-challenge-refresh
```

Run the focused A4/A5 evidence-boundary matrix:

```bash
make hosted-boundary-refresh
```

Run the focused A5/A6 relation-boundary matrix:

```bash
make hosted-relation-boundary-refresh
```

Run the repeated A5/A6 relation-boundary matrix:

```bash
make hosted-relation-boundary-repeats-refresh
```

Run the repeated A6/A7 structured relation-gate matrix:

```bash
make hosted-relation-gate-repeats-refresh
```

Run the repeated A6/A7 expanded boundary matrix:

```bash
make hosted-relation-gate-expanded-repeats-refresh
```

Run the repeated A7/A8 expanded classifier-gate matrix:

```bash
make hosted-relation-classifier-expanded-repeats-refresh
```

Run the repeated A9 expanded calibrated classifier-gate matrix:

```bash
make hosted-relation-calibrated-expanded-repeats-refresh
```

Run the local multi-page graph stress benchmark:

```bash
make graph-refresh
```

Run the local long-chain graph stress benchmark:

```bash
make long-graph-refresh
```

Run the local 24-task long-chain v2 graph benchmark:

```bash
make long-graph-v2-refresh
```

Run the repeated hosted graph stress matrix:

```bash
make hosted-graph-repeats-refresh
```

Run the repeated hosted long-chain graph stress matrix:

```bash
make hosted-long-graph-repeats-refresh
```

Run the hosted A10 long-chain preservation follow-up:

```bash
make hosted-long-graph-preservation-repeats-refresh
```

Run the hosted A1/A4/A8/A9/A10 long-chain v2 pilot:

```bash
make hosted-long-graph-v2-pilot-refresh
```

Run the hosted A8/A9/A10 long-chain v2 cross-model replication, defaulting to
`gpt-4-1-mini`:

```bash
make hosted-long-graph-v2-cross-model-repeats-refresh
```

Run the hosted A10 cross-model follow-up, defaulting to `gpt-4-1-mini`:

```bash
make hosted-long-graph-preservation-cross-model-repeats-refresh
```

Run the hosted A8/A9 cross-model long-chain baseline on the same deployment:

```bash
make hosted-long-graph-relation-gates-cross-model-repeats-refresh
```

Regenerate the paired A7/A8/A9 statistical appendix from the hosted result
files:

```bash
make paired-analysis-a7-a9
```

Regenerate the paired long-graph v2 preservation appendix from the hosted
primary and cross-model result files:

```bash
make paired-analysis-long-graph-v2-preservation
```

Regenerate the qualitative long-graph v2 preservation repair casebook from the
same hosted rows and page corpus:

```bash
make casebook-long-graph-v2-preservation
```

Regenerate the long-graph v2 page-label transition appendix from the same
hosted rows and page corpus:

```bash
make transition-analysis-long-graph-v2-preservation
```

Regenerate the deterministic artifact checksum manifest:

```bash
make artifact-manifest-refresh
```

Hosted targets stream each row to `results.jsonl` and resume by default. To
replace a hosted run intentionally, pass `HOSTED_RESUME=`.

## Committed Snapshots

The committed aggregate snapshots are:

- `docs/hosted-full-summary.md`
- `docs/hosted-challenge-summary.md`
- `docs/hosted-strict-challenge-summary.md`
- `docs/hosted-boundary-summary.md`
- `docs/hosted-relation-boundary-summary.md`
- `docs/hosted-relation-boundary-repeats-summary.md`
- `docs/hosted-relation-gate-repeats-summary.md`
- `docs/hosted-relation-gate-expanded-summary.md`
- `docs/hosted-relation-classifier-expanded-summary.md`
- `docs/hosted-relation-calibrated-expanded-summary.md`
- `docs/paired-a7-a9-analysis.md`
- `docs/paired-long-graph-v2-preservation-analysis.md`
- `docs/long-graph-v2-preservation-casebook.md`
- `docs/long-graph-v2-preservation-transition-analysis.md`
- `docs/research-artifact-manifest.md`
- `docs/hosted-graph-summary.md`
- `docs/hosted-long-graph-summary.md`
- `docs/hosted-long-graph-preservation-summary.md`
- `docs/hosted-long-graph-v2-summary.md`
- `docs/hosted-long-graph-v2-cross-model-summary.md`

Manual audit labels are committed in:

- `data/manual-audit.hosted-challenge.jsonl`
- `data/manual-audit.hosted-strict-challenge.jsonl`
- `data/manual-audit.hosted-a8-a9-boundary.jsonl`

The dashboard in `static/research-dashboard.html` uses only committed aggregate
values. It does not load raw hosted rows or external assets.
