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

Regenerate the paired A7/A8/A9 statistical appendix from the hosted result
files:

```bash
make paired-analysis-a7-a9
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

Manual audit labels are committed in:

- `data/manual-audit.hosted-challenge.jsonl`
- `data/manual-audit.hosted-strict-challenge.jsonl`

The dashboard in `static/research-dashboard.html` uses only committed aggregate
values. It does not load raw hosted rows or external assets.
