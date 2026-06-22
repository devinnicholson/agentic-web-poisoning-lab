# Azure Spend Plan

The project has access to student credits, but the goal is research value, not
spending. Use hosted calls after the local harness is strong.

## Recommended Budget

| Phase | Cap | Purpose | Stop Rule |
| --- | ---: | --- | --- |
| Local harness | $0 | Build deterministic benchmark and report. | Stop if tests or dataset checks fail. |
| Hosted smoke | $5 | One benign and one attacked task under A1. | Stop after two repeated provider/config failures. |
| Focused hosted sweep | $20 | 6 to 10 high-signal tasks under A1 and A4. | Stop if provider blocks dominate and no answer traces remain. |
| Full hosted synthetic sweep | $40 | 30 tasks under A0-A4. | Stop if current spend reaches 60% of available credits. |
| Demo polish | $10 | Optional static hosting or final smoke tests. | Do not run live calls during the presentation. |
| Reserve | $25 | Delayed metering, reruns, or the next adjacent project. | Spend only for a clear research question. |

## Resources

- Azure OpenAI or Foundry model deployment for hosted generation.
- Azure AI Search for page retrieval.
- Azure AI Content Safety Prompt Shields for user and page screening.
- Optional lightweight static hosting for the final demo.

## Hosted Smoke Command

Copy `.env.example` to `.env`, fill the Azure OpenAI endpoint, API key, and
deployment name, then run:

```bash
make hosted-smoke-refresh
```

The default smoke run evaluates `task_011` and `task_025` under
`A1_AGENT_BASELINE` and `A4_FULL_DEFENSE`. Results, report, and audit queue are
written under `experiments/results/hosted-smoke/` and stay out of Git.

The Make target uses an 8-second delay between hosted calls by default to avoid
student deployment rate limits. Override it when needed:

```bash
HOSTED_DELAY_SECONDS=12 make hosted-smoke-refresh
```

After the smoke run succeeds, run the focused sweep:

```bash
make hosted-focused-refresh
```

The focused sweep runs 8 tasks under `A1_AGENT_BASELINE`,
`A3_PROMPT_SHIELDS`, and `A4_FULL_DEFENSE`, for 24 hosted calls. It writes the
same hosted report and audit queue plus `comparison.md`, which pairs hosted rows
with deterministic local rows.

Hosted calls retry transient 429/5xx failures before recording a provider-error
row. Tune retry behavior with `AZURE_OPENAI_MAX_RETRIES` and
`AZURE_OPENAI_RETRY_BASE_SECONDS` in `.env`.

For the first research-grade run, use the full hosted matrix:

```bash
make hosted-full-refresh
```

This runs all 30 tasks under A0-A4 for 150 hosted calls. It regenerates local
baseline outputs first, then writes hosted `report.md`, `audit-queue.md`,
`comparison.md`, and `stats.md` under `experiments/results/hosted-full/`.
The `stats.md` file is the key quantitative readout because it includes Wilson
confidence intervals, attack-class tables, paired defense deltas, abstention
calibration, and provider retry/token totals.

Hosted Make targets pass `--resume` by default, so long runs append each row to
`results.jsonl` and skip completed task/condition pairs when rerun. To force a
fresh hosted run, clear the Make variable:

```bash
HOSTED_RESUME= make hosted-full-refresh
```

## Cost Controls

- Keep pages short and synthetic.
- Cache page embeddings.
- Cap cases per hosted run.
- Use `HOSTED_DELAY_SECONDS` if the deployment has low request limits.
- Move to the full matrix only after the focused sweep has clean provider
  outcomes.
- Keep raw hosted outputs under `experiments/results/`.
- Track current budget after each hosted phase.
- Stop the smoke phase after two repeated provider/config failures.
