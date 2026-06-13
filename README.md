# Agentic Web Poisoning Lab

Research and demo repo for testing whether agentic AI systems stay reliable
when external web-like pages contain adversarial, misleading, stale, or
source-laundered content.

This is the sibling project to `rag-redteam-lab`. The RAG project showed that
retrieved evidence can corrupt answers and citations. This project moves the
same research theme into an agentic setting: the system can browse, select
sources, synthesize evidence, and decide when to abstain.

## Research Question

Do agentic AI systems remain reliable when the external pages they inspect
contain prompt injections, source laundering, stale policy text, fake citations,
or misleading calls to action?

## Why This Is Worth Spending Credits On

- It is current: indirect prompt injection is more serious when agents browse
  and make multi-step decisions.
- It is demoable: the audience can inspect the page, the agent trace, and the
  final answer side by side.
- It has research merit: the evaluation separates final answer correctness,
  source selection, page trust, hidden-instruction exposure, and action safety.
- It reuses lessons from the RAG lab while testing a broader agent workflow.

## Planned Conditions

| Condition | Name | Description |
| --- | --- | --- |
| A0 | Direct answer | Model answers without browsing. |
| A1 | Agent baseline | Agent browses top pages and answers with citations. |
| A2 | Source ranking | Agent prefers trusted/current pages before synthesis. |
| A3 | Prompt Shields | User prompt and page-content screening before synthesis. |
| A4 | Full defense | Source ranking, Prompt Shields, citation validation, and abstention. |

## Attack Classes

- Indirect prompt injection embedded in page text.
- Source laundering through formal-looking but low-trust pages.
- Stale page conflict against a current policy page.
- Fake citation or reference bait.
- Action hijack, where a page tries to make the agent change task goals.
- Confidence pressure, where a page pushes certainty despite weak evidence.

## First Milestone

Build a local deterministic harness with synthetic web pages:

1. Load a task case and a small page corpus.
2. Simulate browsing and page selection.
3. Run A0 through A4.
4. Log page visits, selected evidence, ignored/filtered pages, final answer,
   citations, safety state, and action decisions.
5. Produce a Markdown report and a static demo trace.

## Repo Structure

```text
.
├── data/      # Synthetic web pages and task cases
├── docs/      # Research plan, protocol, budget plan
├── src/       # Harness source
└── tests/     # Unit tests and fixture checks
```

## Current Status

Scaffolded. The first committed artifact is the research plan plus seed
synthetic cases. No Azure spend is required until the local harness is working.

## Safety Rule

Keep all attack pages synthetic and redacted. Public demo artifacts should show
attack mechanisms and outcomes, not reusable operational prompt-injection text.
