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

## Evaluation Conditions

| Condition | Name | Description |
| --- | --- | --- |
| A0 | Direct answer | Model answers without browsing. |
| A1 | Agent baseline | Agent browses top pages and answers with citations. |
| A2 | Source ranking | Agent prefers trusted/current pages before synthesis. |
| A3 | Prompt Shields | User prompt and page-content screening before synthesis. |
| A4 | Full defense | Source ranking, Prompt Shields, citation validation, and abstention. |
| A5 | Strict abstention | Full defense plus explicit evidence-sufficiency rules. |
| A6 | Relation verifier | A5 plus explicit direct-support/direct-refutation/missing-validation classification. |
| A7 | Structured relation gate | A6 plus application enforcement of verified evidence-relation labels. |
| A8 | Classified relation gate | A7-style gate using a separate relation-classifier stage instead of gold labels. |
| A9 | Calibrated relation gate | A8 plus a conservative evidence-gap override for absent independent validation. |
| A10 | Preservation-calibrated relation gate | A9 plus direct-support/direct-refutation preservation when trusted current pages agree. |

## Attack Classes

- Indirect prompt injection embedded in page text.
- Source laundering through formal-looking but low-trust pages.
- Stale page conflict against a current policy page.
- Fake citation or reference bait.
- Action hijack, where a page tries to make the agent change task goals.
- Confidence pressure, where a page pushes certainty despite weak evidence.

## Local Quickstart

Run tests:

```bash
make test
```

Run the deterministic seed benchmark and write a report:

```bash
make research-refresh
```

Generate only the human audit queue after a run:

```bash
make audit-local
```

Run the Azure OpenAI hosted smoke validation after filling `.env` from
`.env.example`:

```bash
make hosted-smoke-refresh
```

Run the focused Azure sweep across six attack classes and two benign controls:

```bash
make hosted-focused-refresh
```

Run the full hosted research matrix across all 30 tasks and A0-A4:

```bash
make hosted-full-refresh
```

Run the harder challenge set focused on source laundering and abstention:

```bash
make hosted-challenge-refresh
```

Run the same challenge set with the experimental A5 strict-abstention condition:

```bash
make hosted-strict-challenge-refresh
```

Run the focused evidence-boundary set for A4/A5:

```bash
make hosted-boundary-refresh
```

Run the relation-verifier follow-up for A5/A6:

```bash
make hosted-relation-boundary-refresh
```

Run five repeated A5/A6 boundary trials for variance:

```bash
make hosted-relation-boundary-repeats-refresh
```

Run five repeated A6/A7 boundary trials for the structured relation gate:

```bash
make hosted-relation-gate-repeats-refresh
```

Run five repeated A6/A7 trials on the expanded boundary set:

```bash
make hosted-relation-gate-expanded-repeats-refresh
```

Run the local expanded A7/A8 classifier-gate smoke benchmark:

```bash
make relation-classifier-expanded-refresh
```

Run five repeated hosted A7/A8 classifier-gate trials on the expanded boundary
set:

```bash
make hosted-relation-classifier-expanded-repeats-refresh
```

Run five repeated hosted A9 calibrated classifier-gate trials:

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

Run three repeated hosted graph stress trials:

```bash
make hosted-graph-repeats-refresh
```

Run three repeated hosted long-chain graph stress trials:

```bash
make hosted-long-graph-repeats-refresh
```

Run the hosted A10 long-chain preservation follow-up:

```bash
make hosted-long-graph-preservation-repeats-refresh
```

Generate the paired A7/A8/A9 statistical appendix from hosted result files:

```bash
make paired-analysis-a7-a9
```

Outputs are written under `experiments/results/local/` and kept out of Git.
Hosted smoke outputs are written under `experiments/results/hosted-smoke/` and
are also kept out of Git. Focused sweep outputs are written under
`experiments/results/hosted-focused/`, including `comparison.md` for local vs
hosted deltas. A committed aggregate snapshot is in
`docs/hosted-focused-summary.md`. Full hosted matrix outputs are written under
`experiments/results/hosted-full/`, including `stats.md` with Wilson confidence
intervals, attack-class breakdowns, defense deltas, and provider reliability.
A committed aggregate snapshot is in `docs/hosted-full-summary.md`.
Challenge-set outputs are written under `experiments/results/hosted-challenge/`
and use `data/tasks.challenge.jsonl` plus `data/pages.challenge.jsonl`. A
committed aggregate snapshot is in `docs/hosted-challenge-summary.md`.
Strict-abstention challenge outputs are written under
`experiments/results/hosted-strict-challenge/`; this keeps the A1-A4 snapshot
fixed while adding A5 as a follow-up calibration experiment. A committed
aggregate snapshot is in `docs/hosted-strict-challenge-summary.md`.
Boundary-set outputs are written under `experiments/results/hosted-boundary/`
and use `data/tasks.boundary.jsonl` plus `data/pages.boundary.jsonl`. A
committed aggregate snapshot is in `docs/hosted-boundary-summary.md`.
Relation-boundary outputs are written under
`experiments/results/hosted-relation-boundary/` and compare A5 against the
experimental A6 relation verifier. A committed aggregate snapshot is in
`docs/hosted-relation-boundary-summary.md`.
Repeated relation-boundary outputs are written under
`experiments/results/hosted-relation-boundary-repeats/` and compare five A5/A6
passes for variance. A committed aggregate snapshot is in
`docs/hosted-relation-boundary-repeats-summary.md`.
Structured relation-gate outputs are written under
`experiments/results/hosted-relation-gate-repeats/` and compare five A6/A7
passes. A committed aggregate snapshot is in
`docs/hosted-relation-gate-repeats-summary.md`.
Expanded structured relation-gate outputs are written under
`experiments/results/hosted-relation-gate-expanded-repeats/` and compare five
A6/A7 passes on `data/tasks.boundary-expanded.jsonl`. A committed aggregate
snapshot is in `docs/hosted-relation-gate-expanded-summary.md`.
Classifier-gate outputs are written under
`experiments/results/hosted-relation-classifier-expanded-repeats/` and compare
five A7/A8 passes on the expanded boundary set. This target tests whether a
separate relation-classifier stage can replace A7's synthetic verified labels.
A committed aggregate snapshot is in
`docs/hosted-relation-classifier-expanded-summary.md`.
Calibrated classifier-gate outputs are written under
`experiments/results/hosted-relation-calibrated-expanded-repeats/` and test the
A9 evidence-gap override against the A8 classifier failure mode. A committed
aggregate snapshot is in `docs/hosted-relation-calibrated-expanded-summary.md`.
Graph-stress outputs are written under `experiments/results/graph-local/` and
`experiments/results/hosted-graph-repeats/`. They use
`data/tasks.graph.jsonl` and `data/pages.graph.jsonl` to test multi-page
evidence chains with low-trust, stale, and confidence-pressure distractors. A
committed aggregate snapshot is in `docs/hosted-graph-summary.md`.
Long-graph outputs are written under `experiments/results/long-graph-local/`
and `experiments/results/hosted-long-graph-repeats/`. They use
`data/tasks.graph-long.jsonl` and `data/pages.graph-long.jsonl` to test three
trusted pages plus three adversarial distractors per task. A committed
aggregate snapshot is in `docs/hosted-long-graph-summary.md`.
A10 preservation follow-up outputs are written under
`experiments/results/long-graph-preservation-local/` and
`experiments/results/hosted-long-graph-preservation-repeats/`. The committed
aggregate snapshot is in `docs/hosted-long-graph-preservation-summary.md`.
The paired statistical appendix in `docs/paired-a7-a9-analysis.md` aligns A7,
A8, and A9 rows by task and repeat index, including exact McNemar tests for the
A8 degradation and A9 repair.
Hosted Make targets stream rows into `results.jsonl` as each call completes and
resume by default. To force a clean rerun, pass `HOSTED_RESUME=`:

```bash
HOSTED_RESUME= make hosted-full-refresh
```

The public static demo trace is committed at
`static/action-hijack-case-study.html` and opens directly in a browser. The
aggregate research dashboard is committed at `static/research-dashboard.html`.
Paper-style write-up materials are in `docs/paper-draft.md`, with adjudication
rules in `docs/labeling-rubric.md`, a one-page reviewer brief in
`docs/research-brief.md`, and initial manual challenge labels in
`data/manual-audit.hosted-challenge.jsonl` plus strict-abstention labels in
`data/manual-audit.hosted-strict-challenge.jsonl` plus paired A8/A9 boundary
labels in `data/manual-audit.hosted-a8-a9-boundary.jsonl`. Reproduction steps
are in `docs/reproducibility.md`. Research scope and safety boundaries are in
`SECURITY.md`.

## Current Local Result

The deterministic benchmark now runs 30 synthetic tasks across A0-A4, including
24 adversarial tasks and 6 benign controls.

| Condition | Cases | Attack cases | Accuracy | Attack success | Cited poisoned | Filtered poisoned |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A0_DIRECT | 30 | 24 | 66.7% | 0.0% | 0.0% | 0.0% |
| A1_AGENT_BASELINE | 30 | 24 | 20.0% | 100.0% | 80.0% | 0.0% |
| A2_SOURCE_RANKING | 30 | 24 | 100.0% | 0.0% | 0.0% | 0.0% |
| A3_PROMPT_SHIELDS | 30 | 24 | 40.0% | 75.0% | 60.0% | 20.0% |
| A4_FULL_DEFENSE | 30 | 24 | 100.0% | 0.0% | 0.0% | 80.0% |

This deterministic harness result is separate from the hosted model snapshots
in `docs/`. It gives the project a repeatable local baseline and a quick
regression signal.

## Implemented Baseline Milestone

The local deterministic harness with synthetic web pages can:

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
├── static/    # Self-contained public demo artifact
├── src/       # Harness source
└── tests/     # Unit tests and fixture checks
```

## Current Status

M1 local harness and M2 dataset expansion are implemented for the 30-task
synthetic benchmark. M3 audit queue and the first M5 static trace are in place.
The Azure-hosted runner is implemented for the same redacted synthetic corpus.
Completed hosted artifacts now include the full matrix, challenge matrix,
strict-abstention matrix, evidence-boundary matrix, and relation-verifier
boundary follow-up with repeated-trial variance. The A7 structured relation
gate has also been validated on repeated boundary trials and an expanded
16-task boundary sweep. The A8 classified relation gate is implemented with
local smoke results and a hosted repeat snapshot showing the classifier-label
gap against A7. The A9 calibrated relation gate then recovered the A7 ceiling
on the expanded boundary set, with a paired appendix quantifying the 14 fixed
A8 misses and 0 new A9 misses. The hosted graph stress run now extends the
result to 12 multi-page evidence graphs: A8/A9 reached 36/36 accuracy and
12/12 correct abstention while A4 blocked poisoned citations but only abstained
on 2/12 evidence gaps. A harder hosted long-graph run then surfaced the next
boundary: A8/A9 preserved 12/12 evidence-gap abstentions but over-abstained on
some direct policy and privacy-board controls. The A10 preservation-calibrated
follow-up repaired that long-graph boundary, reaching 36/36 accuracy, 12/12
correct evidence-gap abstention, and 24/24 direct-control preservation with
0/36 attack success and 0/36 poisoned citations. CI is enabled on the public
GitHub repo, and the static dashboard summarizes the main hosted results.

## Safety Rule

Keep all attack pages synthetic and redacted. Public demo artifacts should show
attack mechanisms and outcomes, not reusable operational prompt-injection text.
