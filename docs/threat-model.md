# Threat Model and Safety Scope

This project studies agentic web poisoning in a synthetic research setting. It
does not provide instructions for compromising real websites, real users, or
production AI systems.

## System Under Test

The evaluated system is an agentic retrieval workflow that reads a small web
corpus, selects evidence pages, and answers policy-style questions. In the
long-graph v2 setting, each task has:

- 4 trusted current evidence pages,
- 4 adversarial distractor pages,
- one expected answer: `yes`, `no`, or `insufficient_evidence`,
- repeated hosted runs across multiple defense conditions.

The corpus is synthetic. Page IDs, tasks, policies, and organizations are
invented for controlled measurement.

## Adversary

The adversary controls low-trust or stale pages in the synthetic corpus. The
adversary tries to cause the agent to cite poisoned evidence, follow stale
claims, over-trust confidence language, or accept fake-citation laundering.

The modeled attack families are:

| Attack family | Synthetic behavior |
| --- | --- |
| Source laundering | Low-trust pages describe a false claim as if it were already validated elsewhere. |
| Stale-page conflict | Old pages conflict with current trusted policy pages. |
| Confidence pressure | Distractors use strong certainty language to pressure selection. |
| Fake citation | Distractors claim external audit or review support that is not present in trusted pages. |

## Defender Goals

The defender should:

1. Avoid citing poisoned or stale evidence.
2. Abstain when trusted current evidence is genuinely insufficient.
3. Preserve useful yes/no answers when trusted current evidence directly
   supports or refutes the proposition.
4. Keep row-level evidence paths inspectable.

The v2 preservation result focuses on goal 3. Earlier relation gates achieved
goals 1 and 2 but sometimes over-abstained on direct controls. A10 adds
preservation calibration to restore direct yes/no answers without relaxing
evidence-gap abstention in the paired rows.

## Out of Scope

This repo does not model:

- arbitrary real websites,
- browser exploitation,
- credential theft,
- cross-site scripting,
- data exfiltration,
- automated account abuse,
- live search-engine manipulation,
- production incident response.

The hosted runs call a model API on synthetic text only. They do not crawl the
public web and do not execute external page content.

## Public Release Boundary

The public artifacts include synthetic tasks, synthetic pages, sanitized hosted
rows, aggregate reports, row-level casebooks, and validation metadata. Provider
hostnames, response IDs, and service fingerprints are redacted from the public
row snapshots.

Private raw run directories under `experiments/results/` remain generated
output. The committed public snapshots under `artifacts/long-graph-v2/` are the
review surface.

## Expected Research Use

Appropriate uses include:

- reproducing aggregate metrics from the committed public rows,
- reviewing row-level evidence paths,
- comparing defense conditions on the synthetic corpus,
- adapting the benchmark harness to other synthetic corpora,
- testing whether the preservation tradeoff replicates across other models.

Inappropriate uses include:

- using the examples as operational guidance for poisoning real sites,
- claiming production robustness from this controlled benchmark alone,
- removing the synthetic-data framing when presenting the result.

## Remaining Risk

Even synthetic examples can normalize adversarial patterns. The repo mitigates
that risk by keeping the attacks abstract, avoiding real targets, documenting
limitations, and emphasizing defensive evaluation. Future public releases should
keep the same boundary: publish enough detail for scientific review without
turning the benchmark into an operational abuse guide.
