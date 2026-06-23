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

Manual audit labels are committed in:

- `data/manual-audit.hosted-challenge.jsonl`
- `data/manual-audit.hosted-strict-challenge.jsonl`

The dashboard in `static/research-dashboard.html` uses only committed aggregate
values. It does not load raw hosted rows or external assets.
