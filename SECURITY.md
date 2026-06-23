# Security and Research Scope

This repository is a synthetic research lab for studying agentic web poisoning,
source laundering, stale-page conflicts, fake citations, and abstention
calibration.

## Scope

In scope:

- Redacted synthetic pages under `data/`.
- Local deterministic benchmark code under `src/`.
- Hosted validation against the synthetic corpus only.
- Defensive analysis of source selection, citation quality, abstention, and
  action safety.

Out of scope:

- Testing against real websites without permission.
- Publishing operational prompt-injection payloads for real services.
- Automated exploitation of live agents, accounts, or browsing systems.
- Instructions designed to bypass a third-party model or application in
  production.

## Reporting Issues

Open a GitHub issue for bugs in the benchmark, labels, metrics, or static
artifacts. Do not include secrets, API keys, or private hosted result files.

If an issue involves a real service or live deployment, report it through that
service's security process instead of posting details here.

## Data Handling

Generated hosted outputs are ignored under `experiments/results/`. Committed
summaries and manual audit labels contain aggregate or synthetic information
only. Local `.env` files are ignored and must not be committed.
