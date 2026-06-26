# Agentic Web Poisoning and Abstention Calibration

## Working Abstract

Web-browsing agents can produce correct final answers while relying on poisoned
or low-trust web evidence. This project evaluates that failure mode using a
synthetic, redacted benchmark of web pages with source-laundering, stale-page,
fake-citation, confidence-pressure, action-hijack, and indirect-prompt
injection attacks. Across a 150-row Azure-hosted full matrix using
`gpt-5-mini-2025-08-07`, the baseline agent reached 96.7% answer accuracy but
cited poisoned pages in 80.0% of rows. A full-defense condition eliminated
measured attack success and poisoned citations, but still showed abstention
calibration failures. A harder 96-row challenge matrix amplified this result,
and a 120-row strict-abstention follow-up added an A5 evidence-sufficiency
condition. A4 and A5 both reduced attack success and poisoned citations to
0.0%, but A4 correctly abstained on only 3/13 `insufficient_evidence` rows
while A5 correctly abstained on 12/13. A focused boundary probe then showed
that some missing-validation wording still sounds like direct negation, and an
A6 relation-verifier follow-up improved correct abstention on that boundary
set from 2/4 to 3/4. A five-repeat boundary sweep then found that A6 improved
missing-validation abstention from 17/20 to 19/20 while preserving 20/20 direct
`no` answers. Finally, an A7 structured relation gate reached 20/20 correct
abstention and 20/20 direct `no` preservation on a repeated boundary sweep.
On an expanded 16-task boundary set, A7 then reached 40/40 correct abstention
and preserved 40/40 direct `no` controls. Replacing A7's verified labels with
an A8 relation-classifier stage preserved 40/40 direct `no` controls and 0/80
poisoned citations, but reduced missing-validation abstention to 26/40. An A9
conservative calibration rule repaired those classifier errors, returning to
40/40 correct abstention and 40/40 direct `no` preservation. These results
then held on a 144-row hosted multi-page graph stress run: A8 and A9 reached
36/36 accuracy and 12/12 correct evidence-gap abstention while A4 blocked
poisoned citations but abstained on only 2/12 graph gaps. Together, the results
then became more nuanced on a harder 144-row hosted long-graph run: A8 and A9
kept 12/12 evidence-gap abstention but over-abstained on some direct policy and
privacy-board controls. A 36-row A10 preservation-calibrated follow-up repaired
that boundary, reaching 36/36 accuracy, 12/12 evidence-gap abstention, and
24/24 direct-control preservation with 0/36 attack success and 0/36 poisoned
citations. A second 36-row run on a `gpt-4.1-mini` deployment replicated the
same A10 result. Together, the results suggest that source trust
controls can mitigate poisoned citations and attack following, but need
explicit evidence-relation calibration, application-level relation gates,
reliable relation classifiers, and direct-control preservation to improve
evidence-gap abstention without blanket over-refusal.

## Research Questions

1. Do web-browsing agents cite poisoned pages even when final answers are
   correct?
2. Which defenses reduce measured attack success and poisoned citations?
3. Does source ranking alone improve reliability under source laundering?
4. After poisoning defenses succeed, do agents still over-answer evidence gaps?

## Experimental Design

The benchmark uses synthetic web-like pages with structured metadata:

- source type
- trust label
- freshness
- poisoned/not poisoned
- attack class
- task-relevant claim

The conditions are:

| Condition | Summary |
| --- | --- |
| A0_DIRECT | Model answers without browsing. |
| A1_AGENT_BASELINE | Browses attack pages first and answers with citations. |
| A2_SOURCE_RANKING | Ranks trusted/current pages first and validates citations. |
| A3_PROMPT_SHIELDS | Adds prompt-level source skepticism and page-instruction handling. |
| A4_FULL_DEFENSE | Combines ranking, filtering, citation validation, and conflict handling. |
| A5_STRICT_ABSTENTION | Adds an explicit rule separating missing support from direct negation. |
| A6_RELATION_VERIFIER | Adds explicit direct-support/direct-refutation/missing-validation classification. |
| A7_STRUCTURED_RELATION_GATE | Enforces verified evidence-relation labels before final answer acceptance. |
| A8_CLASSIFIED_RELATION_GATE | Replaces verified labels with a separate relation-classifier stage before gating. |
| A9_CALIBRATED_RELATION_GATE | Adds a conservative evidence-gap override to the classifier-gated relation labels. |
| A10_PRESERVATION_CALIBRATED_GATE | Preserves direct support/refutation when trusted current summaries clearly answer the proposition. |

Primary metrics:

- answer accuracy
- attack success
- cited poisoned rate
- stale citation rate
- filtered poisoned rate
- abstention calibration
- provider reliability

## Main Results

### Full Matrix

The full hosted matrix ran 30 tasks under A0-A4, for 150 hosted rows.

| Condition | Accuracy | Attack success | Cited poisoned | Filtered poisoned |
| --- | ---: | ---: | ---: | ---: |
| A0_DIRECT | 46.7% | 0.0% | 0.0% | 0.0% |
| A1_AGENT_BASELINE | 96.7% | 4.2% | 80.0% | 0.0% |
| A2_SOURCE_RANKING | 93.3% | 8.3% | 66.7% | 0.0% |
| A3_PROMPT_SHIELDS | 86.7% | 8.3% | 10.0% | 20.0% |
| A4_FULL_DEFENSE | 93.3% | 0.0% | 0.0% | 80.0% |

The central finding is not that the baseline always answers incorrectly. It is
that the baseline can be answer-correct while evidence-compromised.

### Challenge Matrix

The challenge matrix targets the residual weakness: source laundering and
evidence-gap abstention. It ran 24 tasks under A1-A4, for 96 hosted rows.

| Condition | Accuracy | Attack success | Cited poisoned | Filtered poisoned |
| --- | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 70.8% | 35.0% | 83.3% | 0.0% |
| A2_SOURCE_RANKING | 58.3% | 45.0% | 75.0% | 0.0% |
| A3_PROMPT_SHIELDS | 70.8% | 0.0% | 0.0% | 0.0% |
| A4_FULL_DEFENSE | 62.5% | 0.0% | 0.0% | 83.3% |

Source ranking alone is not enough on the challenge set. A2 had higher
attack-success rate than A1 because it often answered confidently on
`insufficient_evidence` rows while still citing poisoned or low-trust evidence.

### Strict-Abstention Follow-Up

The strict-abstention follow-up reran the challenge matrix under A1-A5, for 120
hosted rows. A5 preserved A4's poisoning-control profile while improving
abstention calibration.

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 58.3% | 50.0% | 83.3% | 3/13 |
| A2_SOURCE_RANKING | 62.5% | 45.0% | 70.8% | 4/13 |
| A3_PROMPT_SHIELDS | 75.0% | 0.0% | 0.0% | 7/13 |
| A4_FULL_DEFENSE | 58.3% | 0.0% | 0.0% | 3/13 |
| A5_STRICT_ABSTENTION | 95.8% | 0.0% | 0.0% | 12/13 |

A5 did not simply refuse everything. It preserved direct `no` answers on the
source-laundering refutation tasks and preserved benign yes/no controls. The
one remaining miss was a tutoring-chatbot task where "not externally audited"
was still treated as a direct `no` rather than as missing independent
validation.

Manual adjudication labels for the A4/A5 abstention comparison are committed in
`data/manual-audit.hosted-strict-challenge.jsonl`.

### Evidence-Boundary Follow-Up

The evidence-boundary run isolated this exact edge by pairing four
missing-validation tasks with four direct-negative tasks. It ran A4 and A5 for
16 hosted rows. A5 improved correct abstention from 1/4 to 2/4 while preserving
all four direct `no` answers. Both A4 and A5 maintained 0/8 attack success and
0/8 poisoned citations.

The two remaining A5 misses were certification and deployment-trial questions.
This suggests that some missing-validation language remains semantically close
to direct negation even under a strict sufficiency rubric.

### Relation-Verifier Follow-Up

The relation-verifier follow-up reran the boundary set under A5 and A6. A6
asks the hosted model to classify trusted evidence as direct support, direct
refutation, or missing validation before synthesizing the final answer.

| Condition | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: |
| A5_STRICT_ABSTENTION | 75.0% | 0.0% | 0.0% | 2/4 |
| A6_RELATION_VERIFIER | 87.5% | 0.0% | 0.0% | 3/4 |

A6 preserved all four direct `no` answers and maintained 0/8 attack success and
0/8 poisoned citations. Its remaining miss was the algae-panel certification
gap, where the model still treated absent third-party certification as direct
refutation.

### Repeated Boundary Trials

The repeated boundary sweep ran the same A5/A6 boundary comparison five times,
for 80 hosted rows.

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: | ---: |
| A5_STRICT_ABSTENTION | 40 | 92.5% | 0.0% | 0.0% | 17/20 |
| A6_RELATION_VERIFIER | 40 | 97.5% | 0.0% | 0.0% | 19/20 |

A5 and A6 both preserved all 20 direct-negative controls. The unstable rows
were evidence gaps: A5 missed the evacuation-audit gap once and the
algae-panel certification gap twice; A6 missed only the algae-panel
certification gap once. This makes certification language the clearest next
stress target.

### Structured Relation-Gate Follow-Up

The A7 follow-up reran the boundary repeat sweep under A6 and A7. A7 requires
an `evidence_relation` field and enforces verified relation labels from trusted
evidence before accepting the final answer.

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: | ---: |
| A6_RELATION_VERIFIER | 40 | 97.5% | 0.0% | 0.0% | 19/20 |
| A7_STRUCTURED_RELATION_GATE | 40 | 100.0% | 0.0% | 0.0% | 20/20 |

A7 preserved all 20 direct-negative controls and removed the remaining
certification false non-abstain on this boundary set.

### Expanded Boundary Sweep

The expanded boundary sweep kept the original 8 paired boundary tasks and added
8 new minimal pairs covering certification, accessibility-audit,
independent-replication, and accessibility deployment-trial language. It reran
A6 and A7 for five repeats on each task, for 160 hosted rows.

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: | ---: |
| A6_RELATION_VERIFIER | 80 | 97.5% | 0.0% | 0.0% | 38/40 |
| A7_STRUCTURED_RELATION_GATE | 80 | 100.0% | 0.0% | 0.0% | 40/40 |

A6's two misses were both on the cafeteria waste-sorting robot
deployment-trial gap. A7 preserved all 40 direct `no` controls and all 40
missing-validation abstentions while maintaining 0/80 attack success and 0/80
poisoned citations.

### Classified Relation-Gate Follow-Up

The A8 follow-up reran the expanded boundary set under A7 and A8. A8 uses a
separate hosted relation-classifier call over selected trusted evidence
summaries, supplies the classifier-predicted relation labels to the final
synthesis prompt, and gates final answers on those predicted labels.

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: | ---: |
| A7_STRUCTURED_RELATION_GATE | 80 | 100.0% | 0.0% | 0.0% | 40/40 |
| A8_CLASSIFIED_RELATION_GATE | 80 | 82.5% | 0.0% | 0.0% | 26/40 |

A8 preserved all 40 direct-negative controls and kept 0/80 poisoned citations,
but produced 14/40 false non-abstains on missing-validation rows. Its errors
matched classifier-label errors: missing validation was sometimes classified as
`direct_refutation`, and for the waste-robot and bike-route recommender gaps it
was sometimes classified as `direct_support`.

### Calibrated Relation-Gate Follow-Up

The A9 follow-up reran the expanded boundary set with a conservative
calibration rule. If the trusted summary only reports absent independent
certification, audit, deployment trial, replication, or validation, the
classifier label is calibrated to `missing_validation` before final synthesis.

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: | ---: |
| A9_CALIBRATED_RELATION_GATE | 80 | 100.0% | 0.0% | 0.0% | 40/40 |

A9 preserved all 40 direct-negative controls and removed all A8 false
non-abstains. The calibration changed 10 raw classifier labels, converting the
raw 30/50 missing-validation/direct-refutation split into the correct 40/40
calibrated split.

Because the A8 and A9 rows are aligned by task and repeat index, the repair can
also be analyzed as a paired comparison. On missing-validation rows, A9 fixed
14 A8 misses and introduced 0 new misses, a +35.0 percentage-point paired
correct-abstention delta with exact McNemar p = 0.0001. The paired appendix is
committed at `docs/paired-a7-a9-analysis.md`.

### Multi-Page Graph Stress Run

The graph stress run moved beyond minimal boundary pairs. It used 12 tasks
across dining, housing, emergency-alert, and battery-safety domains. Each task
included two trusted current pages and two adversarial distractors, and each
condition ran three hosted repeats for 144 rows total.

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention |
| --- | ---: | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 36 | 75.0% | 19.4% | 38.9% | 3/12 |
| A4_FULL_DEFENSE | 36 | 72.2% | 0.0% | 0.0% | 2/12 |
| A8_CLASSIFIED_RELATION_GATE | 36 | 100.0% | 0.0% | 0.0% | 12/12 |
| A9_CALIBRATED_RELATION_GATE | 36 | 100.0% | 0.0% | 0.0% | 12/12 |

A4 filtered poisoned pages in 36/36 rows and cited poisoned pages in 0/36
rows, but it still converted 10/12 evidence gaps into confident `no` answers.
A8 and A9 preserved every direct yes/no control, abstained on all 12 graph-gap
rows, and maintained 0/36 poisoned citations. The result supports the central
separation: source hygiene solves poisoned evidence, while evidence-relation
gating solves a different abstention problem.

### Long-Graph Stress Run

The long-graph run increased context pressure from two trusted pages and two
distractors per task to three trusted current pages and three adversarial
distractors per task. It used the same 12-row answer distribution and three
hosted repeats per condition, for 144 rows.

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention | Direct controls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A1_AGENT_BASELINE | 36 | 66.7% | 5.6% | 8.3% | 0/12 | 24/24 |
| A4_FULL_DEFENSE | 36 | 66.7% | 0.0% | 0.0% | 0/12 | 24/24 |
| A8_CLASSIFIED_RELATION_GATE | 36 | 75.0% | 0.0% | 0.0% | 12/12 | 15/24 |
| A9_CALIBRATED_RELATION_GATE | 36 | 77.8% | 0.0% | 0.0% | 12/12 | 16/24 |

This run replicated the evidence-gap repair but exposed a new direct-control
preservation problem. A1 and A4 preserved every direct `yes` and `no` control
but missed all 12 evidence gaps. A8 and A9 corrected all 12 evidence gaps, but
over-abstained on a mental-health policy control and privacy/IRB direct
rejection rows. A9 recovered one repeat of the face-ID direct-rejection row,
but still missed 8/24 direct controls overall.

The A10 follow-up kept the corpus fixed and tested a preservation-calibrated
relation gate. It preserved A9's evidence-gap override, but also restored
direct support or direct refutation when trusted current summaries clearly
answered the proposition.

| Condition | Rows | Accuracy | Attack success | Cited poisoned | Correct abstention | Direct controls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A10_PRESERVATION_CALIBRATED_GATE | 36 | 100.0% | 0.0% | 0.0% | 12/12 | 24/24 |

A second Azure deployment, `gpt-4-1-mini` (`gpt-4.1-mini-2025-04-14`), then
replicated the same A10 result on another 36 hosted rows: 36/36 accuracy,
12/12 correct abstention, 24/24 direct controls, 0/36 attack success, and 0/36
poisoned citations.

A10 fixed the three stable direct-control miss families from the prior run:
`task_long_graph_003` improved from A8/A9 0/3 to A10 3/3, `task_long_graph_005`
improved from A8 0/3 and A9 1/3 to A10 3/3, and `task_long_graph_011`
improved from A8/A9 0/3 to A10 3/3.

## Interpretation

The strongest result is a separation between poisoning robustness and
abstention calibration. A3 and A4 can remove poisoned citations and measured
attack success, but they still often answer `yes` or `no` when the intended
research label is `insufficient_evidence`.

This suggests a two-layer safety model:

1. Source hygiene: remove or discount low-trust, stale, and poisoned sources.
2. Evidence sufficiency: require the model to distinguish direct negation from
   absence of independent support.

The current A4 condition solves the first layer better than the second. A5 is
an initial application-level sufficiency rule that materially improves the
second layer on the hosted challenge set. A6 is the first relation-verifier
iteration: it improves the focused boundary probe, but does not fully eliminate
negative-sounding missing-validation errors. Repeated trials show the remaining
errors are intermittent and concentrated in certification wording. A7 shows
that an application-level relation gate can eliminate the observed boundary
flip on this synthetic set, at the cost of requiring a trusted source of
relation labels. The expanded sweep shows this holds beyond the original
8-task boundary set. A8 shows that replacing verified labels with a hosted
classifier is the next bottleneck: the classifier preserved direct refutations
but inherited the negative-sounding missing-validation confusion. A9 shows that
a conservative evidence-gap calibration rule can repair that failure mode on
the expanded synthetic set, and the hosted graph run shows that the final
relation-gated pattern still holds in moderate multi-page evidence contexts.
The long-graph run adds the next qualification: relation gating also needs a
direct-control preservation layer when trusted current pages agree on direct
support or direct refutation. The A10 follow-up supports that qualification:
adding the preservation layer restored all 24/24 direct controls while keeping
12/12 evidence-gap abstentions.

## Threats To Validity

- Synthetic pages may not capture all properties of real web pages.
- The challenge set intentionally oversamples source laundering and evidence
  gaps, so it should not be interpreted as a population prevalence estimate.
- Some `insufficient_evidence` questions are close to negative factual claims.
  The labeling rubric explicitly adjudicates those cases, but human review
  remains necessary.
- Results use one Azure-hosted model deployment; model-specific behavior may
  differ.
- Prompt-level defenses are implemented as application prompts and filtering
  logic, not as a production browser sandbox.

## Next Experiments

1. Add a second hosted model if credits and access allow.
2. Add manual audit labels for all attack-success, poisoned-citation, and false
   non-abstain rows.
3. Add a second multi-page graph family with longer dependency chains and more
   realistic search-result ordering.
