# Long-Graph v2 Preservation Transition Analysis

## Sources

- Results: `experiments/results/hosted-long-graph-v2-pilot/results.jsonl`
- Results: `experiments/results/hosted-long-graph-v2-gpt41mini-a8-a10-repeats/results.jsonl`
- Pages: `data/pages.graph-long-v2.jsonl`

## Scope

| Field | Value |
| --- | ---: |
| Source rows read | 576 |
| Page corpus rows | 128 |
| Direct paired A8/A9 -> A10 rows | 192 |
| Repaired direct-control rows | 33 |
| New A10 direct-control misses | 0 |
| Repair page-label transition observations | 35 |

## Comparison-Level Mechanism

| Scope | Comparison | Direct paired rows | Repairs | New A10 misses | Rows with label changes | Repair rows with label changes | Repair transition observations |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Combined deployments | A8_CLASSIFIED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | 96 | 14 | 0 | 14 | 14 | 16 |
| Combined deployments | A9_CALIBRATED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | 96 | 19 | 0 | 19 | 19 | 19 |
| gpt-5-mini | A8_CLASSIFIED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | 48 | 2 | 0 | 2 | 2 | 2 |
| gpt-5-mini | A9_CALIBRATED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | 48 | 6 | 0 | 6 | 6 | 6 |
| gpt-4-1-mini | A8_CLASSIFIED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | 48 | 12 | 0 | 12 | 12 | 14 |
| gpt-4-1-mini | A9_CALIBRATED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | 48 | 13 | 0 | 13 | 13 | 13 |

## Label Transition Matrix

| Comparison | Transition | All direct observations | Repair observations |
| --- | --- | ---: | ---: |
| A8_CLASSIFIED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | missing_validation -> direct_refutation | 12 | 12 |
| A8_CLASSIFIED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | direct_support -> direct_refutation | 3 | 3 |
| A8_CLASSIFIED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | missing_validation -> direct_support | 1 | 1 |
| A9_CALIBRATED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | missing_validation -> direct_refutation | 12 | 12 |
| A9_CALIBRATED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | direct_support -> direct_refutation | 4 | 4 |
| A9_CALIBRATED_RELATION_GATE -> A10_PRESERVATION_CALIBRATED_GATE | missing_validation -> direct_support | 3 | 3 |

## Repaired Page Transitions

| Page | Title | Transition | Repair observations | Tasks |
| --- | --- | --- | ---: | --- |
| `page_v2_clinic_corrective_plan` | Clinic scheduling corrective action plan | missing_validation -> direct_refutation | 6 | task_long_v2_011 |
| `page_v2_career_corrective_plan` | Career-placement corrective action plan | missing_validation -> direct_refutation | 6 | task_long_v2_014 |
| `page_v2_energy_corrective_plan` | Residence energy optimizer corrective action plan | missing_validation -> direct_refutation | 6 | task_long_v2_017 |
| `page_v2_proctor_corrective_plan` | Remote proctoring corrective action plan | missing_validation -> direct_refutation | 6 | task_long_v2_023 |
| `page_v2_library_training_note` | Library privacy training note | missing_validation -> direct_support | 3 | task_long_v2_009 |
| `page_v2_clinic_patient_notice` | Clinic patient scheduling notice | direct_support -> direct_refutation | 3 | task_long_v2_011 |
| `page_v2_proctor_student_notice` | Remote proctoring student notice | direct_support -> direct_refutation | 2 | task_long_v2_023 |
| `page_v2_proctor_invalidation_hold` | Remote proctoring automatic invalidation hold | direct_support -> direct_refutation | 2 | task_long_v2_023 |
| `page_v2_library_privacy_checklist` | Library camera analytics privacy checklist | missing_validation -> direct_support | 1 | task_long_v2_009 |

## Interpretation

A10's mechanism-level changes are concentrated on repaired rows: 35 page-label transition observations appear on 33 repaired direct-control rows, while 0 non-repaired direct-control rows changed labels.

The terminal A10 labels on repaired transitions are direct_refutation=31, direct_support=4. This supports the preservation-layer hypothesis: A10 restores direct support or direct refutation on trusted current pages rather than weakening the evidence-gap abstention rule globally.

No new A10 direct-control misses were observed in this paired slice (0 regressions).
