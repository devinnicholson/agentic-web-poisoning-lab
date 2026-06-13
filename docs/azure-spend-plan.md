# Azure Spend Plan

The project has access to student credits, but the goal is research value, not
spending. Use hosted calls after the local harness is strong.

## Recommended Budget

| Phase | Cap | Purpose | Stop Rule |
| --- | ---: | --- | --- |
| Local harness | $0 | Build deterministic benchmark and report. | Stop if tests or dataset checks fail. |
| Hosted smoke | $5 | One benign and one attacked task under A1. | Stop after two repeated provider/config failures. |
| Focused hosted sweep | $20 | 6 to 10 high-signal tasks under A1 and A4. | Stop if provider blocks dominate and no answer traces remain. |
| Full hosted synthetic sweep | $40 | 30 to 50 tasks under A1, A3, and A4. | Stop if current spend reaches 60% of available credits. |
| Demo polish | $10 | Optional static hosting or final smoke tests. | Do not run live calls during the presentation. |
| Reserve | $25 | Delayed metering, reruns, or the next adjacent project. | Spend only for a clear research question. |

## Resources

- Azure OpenAI or Foundry model deployment for hosted generation.
- Azure AI Search for page retrieval.
- Azure AI Content Safety Prompt Shields for user and page screening.
- Optional lightweight static hosting for the final demo.

## Cost Controls

- Keep pages short and synthetic.
- Cache page embeddings.
- Cap cases per hosted run.
- Use `CASE_DELAY_SECONDS` if the deployment has low request limits.
- Keep raw hosted outputs under `experiments/results/`.
- Track current budget after each hosted phase.
