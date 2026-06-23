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
calibration failures. A harder 96-row challenge matrix amplified this result:
A1 and A2 had 35.0% and 45.0% attack-success rates, while A3 and A4 reduced
attack success and poisoned citations to 0.0%. However, A3 and A4 still
over-answered `insufficient_evidence` cases in 7/13 and 9/13 rows,
respectively. These results suggest that source trust controls can mitigate
poisoned citations and attack following, but do not by themselves solve
evidence-gap abstention.

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

## Interpretation

The strongest result is a separation between poisoning robustness and
abstention calibration. A3 and A4 can remove poisoned citations and measured
attack success, but they still often answer `yes` or `no` when the intended
research label is `insufficient_evidence`.

This suggests a two-layer safety model:

1. Source hygiene: remove or discount low-trust, stale, and poisoned sources.
2. Evidence sufficiency: require the model to distinguish direct negation from
   absence of independent support.

The current A4 condition solves the first layer better than the second.

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

1. Add a stricter A5 abstention condition that requires explicit evidence
   sufficiency checks before `yes` or `no`.
2. Run repeated trials on the challenge set to estimate output variance.
3. Add a second hosted model if credits and access allow.
4. Add manual audit labels for all attack-success, poisoned-citation, and false
   non-abstain rows.
5. Convert the static demo into a results dashboard with full-matrix and
   challenge-matrix tabs.
