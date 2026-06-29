# Demo Script

This script is for a 5- to 7-minute walkthrough of the long-graph v2 research
artifact packet.

## Setup

Open these files before the demo:

1. `static/research-dashboard.html`
2. `docs/extended-abstract.md`
3. `docs/paired-long-graph-v2-preservation-analysis.md`
4. `docs/long-graph-v2-preservation-casebook.md`
5. `docs/long-graph-v2-public-artifact-validation.md`
6. `docs/research-artifact-manifest.md`
7. `docs/threat-model.md`

## Talk Track

### 1. Problem

"The problem is not just whether an agent can avoid poisoned web pages. A
defense can look safe by abstaining too often. This project asks whether we can
block poisoned or stale evidence while still preserving useful yes/no answers
when trusted current pages directly answer the question."

Show `docs/extended-abstract.md` and point at the first two paragraphs.

### 2. Corpus

"The corpus is synthetic and controlled: 24 tasks across 8 campus
AI-governance domains. Every task has 4 trusted current pages and 4 adversarial
distractors. That lets us tell apart real evidence gaps from direct support or
direct refutation."

Show the v2 artifact table in `static/research-dashboard.html`, then open
`docs/long-graph-v2-corpus-card.md` if the audience asks for corpus details.

### 3. Main Result

"A8 and A9 solve the obvious poisoning problem: they preserve all evidence-gap
abstentions and avoid poisoned citations. But they over-abstain on direct
controls. A10 preserves abstention where evidence is genuinely insufficient and
restores direct answers where trusted current pages support or refute the
claim."

Point at the dashboard v2 table or the paired analysis scorecard:

| Deployment | Condition | Accuracy | Direct controls | Attack success | Poisoned citations |
| --- | --- | ---: | ---: | ---: | ---: |
| `gpt-5-mini` | A10 | 72/72 | 48/48 | 0/72 | 0/72 |
| `gpt-4.1-mini` | A10 | 72/72 | 48/48 | 0/72 | 0/72 |

### 4. Paired Evidence

"The strongest evidence is paired by deployment, task, and repeat index. Across
both deployments, A10 fixes 14 direct-control rows relative to A8 and 19
relative to A9, with 0 new direct-control misses. The exact McNemar tests are p
= 0.0001 and p < 0.0001 on direct controls."

Open `docs/paired-long-graph-v2-preservation-analysis.md` and show the
combined-deployment rows in "Paired Preservation Tests."

### 5. Row-Level Inspection

"This is not just aggregate scoring. The casebook shows representative repaired
rows and the trusted current pages behind the repair."

Open `docs/long-graph-v2-preservation-casebook.md`. Use any representative case
where A8 or A9 answered `insufficient_evidence` but A10 returned the direct
yes/no label with trusted current citations.

### 6. Reproducibility

"The public rows are committed, sanitized, and machine-validated. The validation
report checks row counts, redaction, summary consistency, condition coverage,
and task/page references. The manifest gives SHA-256 checksums for the public
packet."

Open `docs/long-graph-v2-public-artifact-validation.md`, then
`docs/research-artifact-manifest.md`.

If asked about safety scope, open `docs/threat-model.md` and emphasize that the
corpus is synthetic, the runs do not crawl the public web, and the release
boundary is defensive evaluation.

## Closing

"The claim is deliberately narrow: on a controlled agentic web-poisoning corpus,
preservation calibration separates two goals earlier gates conflated: abstain
when evidence is missing, but answer when trusted current evidence is direct.
The next test is broader replication across corpus generators, model families,
and retrieval stacks."

## Avoid Overclaiming

Do not claim:

- that A10 is robust to all prompt injection or all web poisoning,
- that the synthetic corpus proves production safety,
- that provider behavior will remain stable across future model updates,
- that the experiment covers arbitrary search engines or rerankers.

Do claim:

- the public packet has 576 committed hosted rows,
- both deployments show 72/72 A10 accuracy on the v2 condition rows,
- paired direct-control repairs are concentrated where A8/A9 over-abstained,
- evidence-gap abstention is preserved across all paired evidence-gap rows,
- public artifacts are checksummed and validated from committed files.
