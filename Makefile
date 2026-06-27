PYTHON ?= python
PYTHONPATH ?= src
LOCAL_ENV = PYTHONPATH=$(PYTHONPATH)
HOSTED_DELAY_SECONDS ?= 8
HOSTED_RESUME ?= --resume
FOCUSED_HOSTED_CONDITIONS ?= A1_AGENT_BASELINE,A3_PROMPT_SHIELDS,A4_FULL_DEFENSE
FOCUSED_HOSTED_TASK_IDS ?= task_001,task_002,task_005,task_006,task_011,task_015,task_025,task_027
FULL_HOSTED_CONDITIONS ?= A0_DIRECT,A1_AGENT_BASELINE,A2_SOURCE_RANKING,A3_PROMPT_SHIELDS,A4_FULL_DEFENSE
FULL_HOSTED_TASK_IDS ?= all
CHALLENGE_TASKS ?= data/tasks.challenge.jsonl
CHALLENGE_PAGES ?= data/pages.challenge.jsonl
CHALLENGE_CONDITIONS ?= A1_AGENT_BASELINE,A2_SOURCE_RANKING,A3_PROMPT_SHIELDS,A4_FULL_DEFENSE
CHALLENGE_HOSTED_CONDITIONS ?= $(CHALLENGE_CONDITIONS)
CHALLENGE_HOSTED_TASK_IDS ?= all
STRICT_CHALLENGE_CONDITIONS ?= A1_AGENT_BASELINE,A2_SOURCE_RANKING,A3_PROMPT_SHIELDS,A4_FULL_DEFENSE,A5_STRICT_ABSTENTION
STRICT_CHALLENGE_HOSTED_TASK_IDS ?= all
BOUNDARY_TASKS ?= data/tasks.boundary.jsonl
BOUNDARY_PAGES ?= data/pages.boundary.jsonl
BOUNDARY_EXPANDED_TASKS ?= data/tasks.boundary-expanded.jsonl
BOUNDARY_EXPANDED_PAGES ?= data/pages.boundary-expanded.jsonl
GRAPH_TASKS ?= data/tasks.graph.jsonl
GRAPH_PAGES ?= data/pages.graph.jsonl
LONG_GRAPH_TASKS ?= data/tasks.graph-long.jsonl
LONG_GRAPH_PAGES ?= data/pages.graph-long.jsonl
LONG_GRAPH_V2_TASKS ?= data/tasks.graph-long-v2.jsonl
LONG_GRAPH_V2_PAGES ?= data/pages.graph-long-v2.jsonl
BOUNDARY_CONDITIONS ?= A4_FULL_DEFENSE,A5_STRICT_ABSTENTION
BOUNDARY_HOSTED_TASK_IDS ?= all
RELATION_BOUNDARY_CONDITIONS ?= A5_STRICT_ABSTENTION,A6_RELATION_VERIFIER
RELATION_BOUNDARY_HOSTED_TASK_IDS ?= all
RELATION_BOUNDARY_REPEATS ?= 5
RELATION_GATE_CONDITIONS ?= A6_RELATION_VERIFIER,A7_STRUCTURED_RELATION_GATE
RELATION_CLASSIFIER_CONDITIONS ?= A7_STRUCTURED_RELATION_GATE,A8_CLASSIFIED_RELATION_GATE
RELATION_CALIBRATED_CONDITIONS ?= A9_CALIBRATED_RELATION_GATE
RELATION_GATE_REPEATS ?= 5
GRAPH_CONDITIONS ?= A1_AGENT_BASELINE,A4_FULL_DEFENSE,A8_CLASSIFIED_RELATION_GATE,A9_CALIBRATED_RELATION_GATE
GRAPH_HOSTED_TASK_IDS ?= all
GRAPH_REPEATS ?= 3
GRAPH_HOSTED_DELAY_SECONDS ?= 2
LONG_GRAPH_CONDITIONS ?= A1_AGENT_BASELINE,A4_FULL_DEFENSE,A8_CLASSIFIED_RELATION_GATE,A9_CALIBRATED_RELATION_GATE
LONG_GRAPH_HOSTED_TASK_IDS ?= all
LONG_GRAPH_REPEATS ?= 3
LONG_GRAPH_HOSTED_DELAY_SECONDS ?= 2
LONG_GRAPH_PRESERVATION_CONDITIONS ?= A10_PRESERVATION_CALIBRATED_GATE
LONG_GRAPH_V2_CONDITIONS ?= A1_AGENT_BASELINE,A4_FULL_DEFENSE,A8_CLASSIFIED_RELATION_GATE,A9_CALIBRATED_RELATION_GATE,A10_PRESERVATION_CALIBRATED_GATE
LONG_GRAPH_V2_HOSTED_CONDITIONS ?= $(LONG_GRAPH_V2_CONDITIONS)
LONG_GRAPH_V2_HOSTED_TASK_IDS ?= all
LONG_GRAPH_V2_REPEATS ?= 3
LONG_GRAPH_V2_HOSTED_DELAY_SECONDS ?= 2
LONG_GRAPH_CROSS_MODEL_DEPLOYMENT ?= gpt-4-1-mini
LONG_GRAPH_RELATION_GATES_CROSS_MODEL_CONDITIONS ?= A8_CLASSIFIED_RELATION_GATE,A9_CALIBRATED_RELATION_GATE
LONG_GRAPH_RELATION_GATES_CROSS_MODEL_OUT_DIR ?= experiments/results/hosted-long-graph-gpt41mini-relation-gates-repeats
LONG_GRAPH_RELATION_GATES_CROSS_MODEL_RUN_MODE ?= hosted_long_graph_gpt41mini_relation_gates_repeats
LONG_GRAPH_CROSS_MODEL_OUT_DIR ?= experiments/results/hosted-long-graph-preservation-gpt41mini-network-repeats
LONG_GRAPH_CROSS_MODEL_RUN_MODE ?= hosted_long_graph_preservation_gpt41mini_network_repeats

.PHONY: help test run-local report-local audit-local research-refresh run-challenge-local report-challenge-local audit-challenge-local challenge-refresh run-strict-challenge-local report-strict-challenge-local audit-strict-challenge-local strict-challenge-refresh run-boundary-local report-boundary-local audit-boundary-local boundary-refresh run-relation-boundary-local report-relation-boundary-local audit-relation-boundary-local relation-boundary-refresh run-relation-gate-local report-relation-gate-local audit-relation-gate-local relation-gate-refresh run-relation-gate-expanded-local report-relation-gate-expanded-local audit-relation-gate-expanded-local relation-gate-expanded-refresh run-relation-classifier-expanded-local report-relation-classifier-expanded-local audit-relation-classifier-expanded-local relation-classifier-expanded-refresh run-relation-calibrated-expanded-local report-relation-calibrated-expanded-local audit-relation-calibrated-expanded-local relation-calibrated-expanded-refresh run-graph-local report-graph-local audit-graph-local stats-graph-local graph-refresh run-long-graph-local report-long-graph-local audit-long-graph-local stats-long-graph-local long-graph-refresh run-long-graph-preservation-local report-long-graph-preservation-local audit-long-graph-preservation-local stats-long-graph-preservation-local long-graph-preservation-refresh paired-analysis-a7-a9 run-hosted-graph-repeats report-hosted-graph-repeats audit-hosted-graph-repeats stats-hosted-graph-repeats hosted-graph-repeats-refresh run-hosted-long-graph-repeats report-hosted-long-graph-repeats audit-hosted-long-graph-repeats stats-hosted-long-graph-repeats hosted-long-graph-repeats-refresh run-hosted-long-graph-preservation-repeats report-hosted-long-graph-preservation-repeats audit-hosted-long-graph-preservation-repeats stats-hosted-long-graph-preservation-repeats hosted-long-graph-preservation-repeats-refresh run-hosted-long-graph-relation-gates-cross-model-repeats report-hosted-long-graph-relation-gates-cross-model-repeats audit-hosted-long-graph-relation-gates-cross-model-repeats stats-hosted-long-graph-relation-gates-cross-model-repeats hosted-long-graph-relation-gates-cross-model-repeats-refresh run-hosted-long-graph-preservation-cross-model-repeats report-hosted-long-graph-preservation-cross-model-repeats audit-hosted-long-graph-preservation-cross-model-repeats stats-hosted-long-graph-preservation-cross-model-repeats hosted-long-graph-preservation-cross-model-repeats-refresh run-hosted-smoke report-hosted-smoke audit-hosted-smoke hosted-smoke-refresh run-hosted-focused report-hosted-focused audit-hosted-focused compare-hosted-focused hosted-focused-refresh run-hosted-full report-hosted-full audit-hosted-full compare-hosted-full stats-hosted-full hosted-full-refresh run-hosted-challenge report-hosted-challenge audit-hosted-challenge compare-hosted-challenge stats-hosted-challenge hosted-challenge-refresh run-hosted-strict-challenge report-hosted-strict-challenge audit-hosted-strict-challenge compare-hosted-strict-challenge stats-hosted-strict-challenge hosted-strict-challenge-refresh run-hosted-boundary report-hosted-boundary audit-hosted-boundary compare-hosted-boundary stats-hosted-boundary hosted-boundary-refresh run-hosted-relation-boundary report-hosted-relation-boundary audit-hosted-relation-boundary compare-hosted-relation-boundary stats-hosted-relation-boundary hosted-relation-boundary-refresh run-hosted-relation-boundary-repeats report-hosted-relation-boundary-repeats audit-hosted-relation-boundary-repeats stats-hosted-relation-boundary-repeats hosted-relation-boundary-repeats-refresh run-hosted-relation-gate-repeats report-hosted-relation-gate-repeats audit-hosted-relation-gate-repeats stats-hosted-relation-gate-repeats hosted-relation-gate-repeats-refresh run-hosted-relation-gate-expanded-repeats report-hosted-relation-gate-expanded-repeats audit-hosted-relation-gate-expanded-repeats stats-hosted-relation-gate-expanded-repeats hosted-relation-gate-expanded-repeats-refresh run-hosted-relation-classifier-expanded-repeats report-hosted-relation-classifier-expanded-repeats audit-hosted-relation-classifier-expanded-repeats stats-hosted-relation-classifier-expanded-repeats hosted-relation-classifier-expanded-repeats-refresh run-hosted-relation-calibrated-expanded-repeats report-hosted-relation-calibrated-expanded-repeats audit-hosted-relation-calibrated-expanded-repeats stats-hosted-relation-calibrated-expanded-repeats hosted-relation-calibrated-expanded-repeats-refresh
.PHONY: run-long-graph-v2-local report-long-graph-v2-local audit-long-graph-v2-local stats-long-graph-v2-local long-graph-v2-refresh run-hosted-long-graph-v2-pilot report-hosted-long-graph-v2-pilot audit-hosted-long-graph-v2-pilot stats-hosted-long-graph-v2-pilot hosted-long-graph-v2-pilot-refresh

help:
	@printf '%s\n' \
		'Targets:' \
		'  make test             Run unit tests.' \
		'  make run-local        Run the deterministic seed benchmark.' \
		'  make report-local     Generate a Markdown report from local results.' \
		'  make audit-local      Generate a human audit queue from local results.' \
		'  make research-refresh Run local benchmark, report, and audit queue.' \
		'  make challenge-refresh Run hard local challenge benchmark.' \
		'  make strict-challenge-refresh Run hard local challenge benchmark with A5.' \
		'  make boundary-refresh Run local evidence-boundary benchmark.' \
		'  make relation-boundary-refresh Run local A5/A6 relation-boundary benchmark.' \
		'  make relation-gate-refresh Run local A6/A7 relation-gate benchmark.' \
		'  make relation-gate-expanded-refresh Run local expanded A6/A7 relation-gate benchmark.' \
		'  make relation-classifier-expanded-refresh Run local expanded A7/A8 classifier-gate benchmark.' \
		'  make relation-calibrated-expanded-refresh Run local expanded A9 calibrated classifier benchmark.' \
		'  make graph-refresh Run local multi-page graph stress benchmark.' \
		'  make long-graph-refresh Run local long-chain graph stress benchmark.' \
		'  make long-graph-preservation-refresh Run local A10 long-chain graph follow-up.' \
		'  make long-graph-v2-refresh Run local 24-task long-chain v2 graph benchmark.' \
		'  make hosted-graph-repeats-refresh Run hosted repeated graph stress trials.' \
		'  make hosted-long-graph-repeats-refresh Run hosted repeated long-chain graph trials.' \
		'  make hosted-long-graph-preservation-repeats-refresh Run hosted A10 long-chain graph follow-up.' \
		'  make hosted-long-graph-v2-pilot-refresh Run hosted A1/A4/A8/A9/A10 long-chain v2 pilot.' \
		'  make hosted-long-graph-relation-gates-cross-model-repeats-refresh Run hosted A8/A9 cross-model long-chain baseline.' \
		'  make hosted-long-graph-preservation-cross-model-repeats-refresh Run hosted A10 cross-model long-chain follow-up.' \
		'  make hosted-smoke-refresh Run Azure hosted smoke, report, and audit queue.' \
		'  make hosted-focused-refresh Run focused Azure sweep, reports, and audit queue.' \
		'  make hosted-full-refresh Run full Azure matrix with comparison and stats.' \
		'  make hosted-challenge-refresh Run hard Azure challenge matrix with stats.' \
		'  make hosted-strict-challenge-refresh Run hard Azure challenge matrix with A5.' \
		'  make hosted-boundary-refresh Run hosted A4/A5 evidence-boundary matrix.' \
		'  make hosted-relation-boundary-refresh Run hosted A5/A6 relation-boundary matrix.' \
		'  make hosted-relation-boundary-repeats-refresh Run hosted repeated A5/A6 boundary trials.' \
		'  make hosted-relation-gate-repeats-refresh Run hosted repeated A6/A7 relation-gate trials.' \
		'  make hosted-relation-gate-expanded-repeats-refresh Run hosted repeated expanded A6/A7 trials.' \
		'  make hosted-relation-classifier-expanded-repeats-refresh Run hosted repeated expanded A7/A8 classifier trials.' \
		'  make hosted-relation-calibrated-expanded-repeats-refresh Run hosted repeated expanded A9 calibrated trials.' \
		'  make paired-analysis-a7-a9 Generate paired A7/A8/A9 statistical appendix.'

test:
	$(LOCAL_ENV) $(PYTHON) -m unittest discover -s tests

run-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--out-dir experiments/results/local

report-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/local/results.jsonl \
		--out experiments/results/local/report.md

audit-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/local/results.jsonl \
		--pages data/pages.seed.jsonl \
		--out experiments/results/local/audit-queue.md

research-refresh: run-local report-local audit-local

run-challenge-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(CHALLENGE_TASKS) \
		--pages $(CHALLENGE_PAGES) \
		--conditions $(CHALLENGE_CONDITIONS) \
		--out-dir experiments/results/challenge-local

report-challenge-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/challenge-local/results.jsonl \
		--out experiments/results/challenge-local/report.md

audit-challenge-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/challenge-local/results.jsonl \
		--pages $(CHALLENGE_PAGES) \
		--out experiments/results/challenge-local/audit-queue.md

challenge-refresh: run-challenge-local report-challenge-local audit-challenge-local

run-strict-challenge-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(CHALLENGE_TASKS) \
		--pages $(CHALLENGE_PAGES) \
		--conditions $(STRICT_CHALLENGE_CONDITIONS) \
		--out-dir experiments/results/strict-challenge-local

report-strict-challenge-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/strict-challenge-local/results.jsonl \
		--out experiments/results/strict-challenge-local/report.md

audit-strict-challenge-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/strict-challenge-local/results.jsonl \
		--pages $(CHALLENGE_PAGES) \
		--out experiments/results/strict-challenge-local/audit-queue.md

strict-challenge-refresh: run-strict-challenge-local report-strict-challenge-local audit-strict-challenge-local

run-boundary-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(BOUNDARY_TASKS) \
		--pages $(BOUNDARY_PAGES) \
		--conditions $(BOUNDARY_CONDITIONS) \
		--out-dir experiments/results/boundary-local

report-boundary-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/boundary-local/results.jsonl \
		--out experiments/results/boundary-local/report.md

audit-boundary-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/boundary-local/results.jsonl \
		--pages $(BOUNDARY_PAGES) \
		--out experiments/results/boundary-local/audit-queue.md

boundary-refresh: run-boundary-local report-boundary-local audit-boundary-local

run-relation-boundary-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(BOUNDARY_TASKS) \
		--pages $(BOUNDARY_PAGES) \
		--conditions $(RELATION_BOUNDARY_CONDITIONS) \
		--out-dir experiments/results/relation-boundary-local

report-relation-boundary-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/relation-boundary-local/results.jsonl \
		--out experiments/results/relation-boundary-local/report.md

audit-relation-boundary-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/relation-boundary-local/results.jsonl \
		--pages $(BOUNDARY_PAGES) \
		--out experiments/results/relation-boundary-local/audit-queue.md

relation-boundary-refresh: run-relation-boundary-local report-relation-boundary-local audit-relation-boundary-local

run-relation-gate-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(BOUNDARY_TASKS) \
		--pages $(BOUNDARY_PAGES) \
		--conditions $(RELATION_GATE_CONDITIONS) \
		--out-dir experiments/results/relation-gate-local

report-relation-gate-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/relation-gate-local/results.jsonl \
		--out experiments/results/relation-gate-local/report.md

audit-relation-gate-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/relation-gate-local/results.jsonl \
		--pages $(BOUNDARY_PAGES) \
		--out experiments/results/relation-gate-local/audit-queue.md

relation-gate-refresh: run-relation-gate-local report-relation-gate-local audit-relation-gate-local

run-relation-gate-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(BOUNDARY_EXPANDED_TASKS) \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--conditions $(RELATION_GATE_CONDITIONS) \
		--out-dir experiments/results/relation-gate-expanded-local

report-relation-gate-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/relation-gate-expanded-local/results.jsonl \
		--out experiments/results/relation-gate-expanded-local/report.md

audit-relation-gate-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/relation-gate-expanded-local/results.jsonl \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--out experiments/results/relation-gate-expanded-local/audit-queue.md

relation-gate-expanded-refresh: run-relation-gate-expanded-local report-relation-gate-expanded-local audit-relation-gate-expanded-local

run-relation-classifier-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(BOUNDARY_EXPANDED_TASKS) \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--conditions $(RELATION_CLASSIFIER_CONDITIONS) \
		--out-dir experiments/results/relation-classifier-expanded-local

report-relation-classifier-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/relation-classifier-expanded-local/results.jsonl \
		--out experiments/results/relation-classifier-expanded-local/report.md

audit-relation-classifier-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/relation-classifier-expanded-local/results.jsonl \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--out experiments/results/relation-classifier-expanded-local/audit-queue.md

relation-classifier-expanded-refresh: run-relation-classifier-expanded-local report-relation-classifier-expanded-local audit-relation-classifier-expanded-local

run-relation-calibrated-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(BOUNDARY_EXPANDED_TASKS) \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--conditions $(RELATION_CALIBRATED_CONDITIONS) \
		--out-dir experiments/results/relation-calibrated-expanded-local

report-relation-calibrated-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/relation-calibrated-expanded-local/results.jsonl \
		--out experiments/results/relation-calibrated-expanded-local/report.md

audit-relation-calibrated-expanded-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/relation-calibrated-expanded-local/results.jsonl \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--out experiments/results/relation-calibrated-expanded-local/audit-queue.md

relation-calibrated-expanded-refresh: run-relation-calibrated-expanded-local report-relation-calibrated-expanded-local audit-relation-calibrated-expanded-local

run-graph-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(GRAPH_TASKS) \
		--pages $(GRAPH_PAGES) \
		--conditions $(GRAPH_CONDITIONS) \
		--out-dir experiments/results/graph-local

report-graph-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/graph-local/results.jsonl \
		--out experiments/results/graph-local/report.md

audit-graph-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/graph-local/results.jsonl \
		--pages $(GRAPH_PAGES) \
		--out experiments/results/graph-local/audit-queue.md

stats-graph-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/graph-local/results.jsonl \
		--out experiments/results/graph-local/stats.md

graph-refresh: run-graph-local report-graph-local audit-graph-local stats-graph-local

run-long-graph-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(LONG_GRAPH_TASKS) \
		--pages $(LONG_GRAPH_PAGES) \
		--conditions $(LONG_GRAPH_CONDITIONS) \
		--out-dir experiments/results/long-graph-local

report-long-graph-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/long-graph-local/results.jsonl \
		--out experiments/results/long-graph-local/report.md

audit-long-graph-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/long-graph-local/results.jsonl \
		--pages $(LONG_GRAPH_PAGES) \
		--out experiments/results/long-graph-local/audit-queue.md

stats-long-graph-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/long-graph-local/results.jsonl \
		--out experiments/results/long-graph-local/stats.md

long-graph-refresh: run-long-graph-local report-long-graph-local audit-long-graph-local stats-long-graph-local

run-long-graph-preservation-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(LONG_GRAPH_TASKS) \
		--pages $(LONG_GRAPH_PAGES) \
		--conditions $(LONG_GRAPH_PRESERVATION_CONDITIONS) \
		--out-dir experiments/results/long-graph-preservation-local

report-long-graph-preservation-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/long-graph-preservation-local/results.jsonl \
		--out experiments/results/long-graph-preservation-local/report.md

audit-long-graph-preservation-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/long-graph-preservation-local/results.jsonl \
		--pages $(LONG_GRAPH_PAGES) \
		--out experiments/results/long-graph-preservation-local/audit-queue.md

stats-long-graph-preservation-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/long-graph-preservation-local/results.jsonl \
		--out experiments/results/long-graph-preservation-local/stats.md

long-graph-preservation-refresh: run-long-graph-preservation-local report-long-graph-preservation-local audit-long-graph-preservation-local stats-long-graph-preservation-local

run-long-graph-v2-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--tasks $(LONG_GRAPH_V2_TASKS) \
		--pages $(LONG_GRAPH_V2_PAGES) \
		--conditions $(LONG_GRAPH_V2_CONDITIONS) \
		--out-dir experiments/results/long-graph-v2-local

report-long-graph-v2-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/long-graph-v2-local/results.jsonl \
		--out experiments/results/long-graph-v2-local/report.md

audit-long-graph-v2-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/long-graph-v2-local/results.jsonl \
		--pages $(LONG_GRAPH_V2_PAGES) \
		--out experiments/results/long-graph-v2-local/audit-queue.md

stats-long-graph-v2-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/long-graph-v2-local/results.jsonl \
		--out experiments/results/long-graph-v2-local/stats.md

long-graph-v2-refresh: run-long-graph-v2-local report-long-graph-v2-local audit-long-graph-v2-local stats-long-graph-v2-local

paired-analysis-a7-a9:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli paired-analysis \
		--results experiments/results/hosted-relation-classifier-expanded-repeats/results.jsonl experiments/results/hosted-relation-calibrated-expanded-repeats/results.jsonl \
		--out docs/paired-a7-a9-analysis.md

run-hosted-graph-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(GRAPH_TASKS) \
		--pages $(GRAPH_PAGES) \
		--conditions $(GRAPH_CONDITIONS) \
		--task-ids $(GRAPH_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-graph-repeats \
		--delay-seconds $(GRAPH_HOSTED_DELAY_SECONDS) \
		--run-mode hosted_graph_repeats \
		--repeats $(GRAPH_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-graph-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-graph-repeats/results.jsonl \
		--out experiments/results/hosted-graph-repeats/report.md

audit-hosted-graph-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-graph-repeats/results.jsonl \
		--pages $(GRAPH_PAGES) \
		--out experiments/results/hosted-graph-repeats/audit-queue.md

stats-hosted-graph-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-graph-repeats/results.jsonl \
		--out experiments/results/hosted-graph-repeats/stats.md

hosted-graph-repeats-refresh: graph-refresh run-hosted-graph-repeats report-hosted-graph-repeats audit-hosted-graph-repeats stats-hosted-graph-repeats

run-hosted-long-graph-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(LONG_GRAPH_TASKS) \
		--pages $(LONG_GRAPH_PAGES) \
		--conditions $(LONG_GRAPH_CONDITIONS) \
		--task-ids $(LONG_GRAPH_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-long-graph-repeats \
		--delay-seconds $(LONG_GRAPH_HOSTED_DELAY_SECONDS) \
		--run-mode hosted_long_graph_repeats \
		--repeats $(LONG_GRAPH_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-long-graph-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-long-graph-repeats/results.jsonl \
		--out experiments/results/hosted-long-graph-repeats/report.md

audit-hosted-long-graph-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-long-graph-repeats/results.jsonl \
		--pages $(LONG_GRAPH_PAGES) \
		--out experiments/results/hosted-long-graph-repeats/audit-queue.md

stats-hosted-long-graph-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-long-graph-repeats/results.jsonl \
		--out experiments/results/hosted-long-graph-repeats/stats.md

hosted-long-graph-repeats-refresh: long-graph-refresh run-hosted-long-graph-repeats report-hosted-long-graph-repeats audit-hosted-long-graph-repeats stats-hosted-long-graph-repeats

run-hosted-long-graph-preservation-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(LONG_GRAPH_TASKS) \
		--pages $(LONG_GRAPH_PAGES) \
		--conditions $(LONG_GRAPH_PRESERVATION_CONDITIONS) \
		--task-ids $(LONG_GRAPH_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-long-graph-preservation-repeats \
		--delay-seconds $(LONG_GRAPH_HOSTED_DELAY_SECONDS) \
		--run-mode hosted_long_graph_preservation_repeats \
		--repeats $(LONG_GRAPH_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-long-graph-preservation-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-long-graph-preservation-repeats/results.jsonl \
		--out experiments/results/hosted-long-graph-preservation-repeats/report.md

audit-hosted-long-graph-preservation-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-long-graph-preservation-repeats/results.jsonl \
		--pages $(LONG_GRAPH_PAGES) \
		--out experiments/results/hosted-long-graph-preservation-repeats/audit-queue.md

stats-hosted-long-graph-preservation-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-long-graph-preservation-repeats/results.jsonl \
		--out experiments/results/hosted-long-graph-preservation-repeats/stats.md

hosted-long-graph-preservation-repeats-refresh: long-graph-preservation-refresh run-hosted-long-graph-preservation-repeats report-hosted-long-graph-preservation-repeats audit-hosted-long-graph-preservation-repeats stats-hosted-long-graph-preservation-repeats

run-hosted-long-graph-v2-pilot:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(LONG_GRAPH_V2_TASKS) \
		--pages $(LONG_GRAPH_V2_PAGES) \
		--conditions $(LONG_GRAPH_V2_HOSTED_CONDITIONS) \
		--task-ids $(LONG_GRAPH_V2_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-long-graph-v2-pilot \
		--delay-seconds $(LONG_GRAPH_V2_HOSTED_DELAY_SECONDS) \
		--run-mode hosted_long_graph_v2_pilot \
		--repeats $(LONG_GRAPH_V2_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-long-graph-v2-pilot:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-long-graph-v2-pilot/results.jsonl \
		--out experiments/results/hosted-long-graph-v2-pilot/report.md

audit-hosted-long-graph-v2-pilot:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-long-graph-v2-pilot/results.jsonl \
		--pages $(LONG_GRAPH_V2_PAGES) \
		--out experiments/results/hosted-long-graph-v2-pilot/audit-queue.md

stats-hosted-long-graph-v2-pilot:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-long-graph-v2-pilot/results.jsonl \
		--out experiments/results/hosted-long-graph-v2-pilot/stats.md

hosted-long-graph-v2-pilot-refresh: long-graph-v2-refresh run-hosted-long-graph-v2-pilot report-hosted-long-graph-v2-pilot audit-hosted-long-graph-v2-pilot stats-hosted-long-graph-v2-pilot

run-hosted-long-graph-relation-gates-cross-model-repeats:
	AZURE_OPENAI_DEPLOYMENT=$(LONG_GRAPH_CROSS_MODEL_DEPLOYMENT) $(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(LONG_GRAPH_TASKS) \
		--pages $(LONG_GRAPH_PAGES) \
		--conditions $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_CONDITIONS) \
		--task-ids $(LONG_GRAPH_HOSTED_TASK_IDS) \
		--out-dir $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_OUT_DIR) \
		--delay-seconds $(LONG_GRAPH_HOSTED_DELAY_SECONDS) \
		--run-mode $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_RUN_MODE) \
		--repeats $(LONG_GRAPH_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-long-graph-relation-gates-cross-model-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_OUT_DIR)/results.jsonl \
		--out $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_OUT_DIR)/report.md

audit-hosted-long-graph-relation-gates-cross-model-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_OUT_DIR)/results.jsonl \
		--pages $(LONG_GRAPH_PAGES) \
		--out $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_OUT_DIR)/audit-queue.md

stats-hosted-long-graph-relation-gates-cross-model-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_OUT_DIR)/results.jsonl \
		--out $(LONG_GRAPH_RELATION_GATES_CROSS_MODEL_OUT_DIR)/stats.md

hosted-long-graph-relation-gates-cross-model-repeats-refresh: run-hosted-long-graph-relation-gates-cross-model-repeats report-hosted-long-graph-relation-gates-cross-model-repeats audit-hosted-long-graph-relation-gates-cross-model-repeats stats-hosted-long-graph-relation-gates-cross-model-repeats

run-hosted-long-graph-preservation-cross-model-repeats:
	AZURE_OPENAI_DEPLOYMENT=$(LONG_GRAPH_CROSS_MODEL_DEPLOYMENT) $(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(LONG_GRAPH_TASKS) \
		--pages $(LONG_GRAPH_PAGES) \
		--conditions $(LONG_GRAPH_PRESERVATION_CONDITIONS) \
		--task-ids $(LONG_GRAPH_HOSTED_TASK_IDS) \
		--out-dir $(LONG_GRAPH_CROSS_MODEL_OUT_DIR) \
		--delay-seconds $(LONG_GRAPH_HOSTED_DELAY_SECONDS) \
		--run-mode $(LONG_GRAPH_CROSS_MODEL_RUN_MODE) \
		--repeats $(LONG_GRAPH_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-long-graph-preservation-cross-model-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results $(LONG_GRAPH_CROSS_MODEL_OUT_DIR)/results.jsonl \
		--out $(LONG_GRAPH_CROSS_MODEL_OUT_DIR)/report.md

audit-hosted-long-graph-preservation-cross-model-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results $(LONG_GRAPH_CROSS_MODEL_OUT_DIR)/results.jsonl \
		--pages $(LONG_GRAPH_PAGES) \
		--out $(LONG_GRAPH_CROSS_MODEL_OUT_DIR)/audit-queue.md

stats-hosted-long-graph-preservation-cross-model-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results $(LONG_GRAPH_CROSS_MODEL_OUT_DIR)/results.jsonl \
		--out $(LONG_GRAPH_CROSS_MODEL_OUT_DIR)/stats.md

hosted-long-graph-preservation-cross-model-repeats-refresh: run-hosted-long-graph-preservation-cross-model-repeats report-hosted-long-graph-preservation-cross-model-repeats audit-hosted-long-graph-preservation-cross-model-repeats stats-hosted-long-graph-preservation-cross-model-repeats

run-hosted-smoke:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--out-dir experiments/results/hosted-smoke \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		$(HOSTED_RESUME)

report-hosted-smoke:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-smoke/results.jsonl \
		--out experiments/results/hosted-smoke/report.md

audit-hosted-smoke:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-smoke/results.jsonl \
		--pages data/pages.seed.jsonl \
		--out experiments/results/hosted-smoke/audit-queue.md

hosted-smoke-refresh: run-hosted-smoke report-hosted-smoke audit-hosted-smoke

run-hosted-focused:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--conditions $(FOCUSED_HOSTED_CONDITIONS) \
		--task-ids $(FOCUSED_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-focused \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_focused \
		$(HOSTED_RESUME)

report-hosted-focused:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-focused/results.jsonl \
		--out experiments/results/hosted-focused/report.md

audit-hosted-focused:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-focused/results.jsonl \
		--pages data/pages.seed.jsonl \
		--out experiments/results/hosted-focused/audit-queue.md

compare-hosted-focused:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli compare \
		--local experiments/results/local/results.jsonl \
		--hosted experiments/results/hosted-focused/results.jsonl \
		--out experiments/results/hosted-focused/comparison.md

hosted-focused-refresh: run-hosted-focused report-hosted-focused audit-hosted-focused compare-hosted-focused

run-hosted-full:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--conditions $(FULL_HOSTED_CONDITIONS) \
		--task-ids $(FULL_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-full \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_full \
		$(HOSTED_RESUME)

report-hosted-full:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-full/results.jsonl \
		--out experiments/results/hosted-full/report.md

audit-hosted-full:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-full/results.jsonl \
		--pages data/pages.seed.jsonl \
		--out experiments/results/hosted-full/audit-queue.md

compare-hosted-full:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli compare \
		--local experiments/results/local/results.jsonl \
		--hosted experiments/results/hosted-full/results.jsonl \
		--out experiments/results/hosted-full/comparison.md

stats-hosted-full:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-full/results.jsonl \
		--out experiments/results/hosted-full/stats.md

hosted-full-refresh: research-refresh run-hosted-full report-hosted-full audit-hosted-full compare-hosted-full stats-hosted-full

run-hosted-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(CHALLENGE_TASKS) \
		--pages $(CHALLENGE_PAGES) \
		--conditions $(CHALLENGE_HOSTED_CONDITIONS) \
		--task-ids $(CHALLENGE_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-challenge \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_challenge \
		$(HOSTED_RESUME)

report-hosted-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-challenge/results.jsonl \
		--out experiments/results/hosted-challenge/report.md

audit-hosted-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-challenge/results.jsonl \
		--pages $(CHALLENGE_PAGES) \
		--out experiments/results/hosted-challenge/audit-queue.md

compare-hosted-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli compare \
		--local experiments/results/challenge-local/results.jsonl \
		--hosted experiments/results/hosted-challenge/results.jsonl \
		--out experiments/results/hosted-challenge/comparison.md

stats-hosted-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-challenge/results.jsonl \
		--out experiments/results/hosted-challenge/stats.md

hosted-challenge-refresh: challenge-refresh run-hosted-challenge report-hosted-challenge audit-hosted-challenge compare-hosted-challenge stats-hosted-challenge

run-hosted-strict-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(CHALLENGE_TASKS) \
		--pages $(CHALLENGE_PAGES) \
		--conditions $(STRICT_CHALLENGE_CONDITIONS) \
		--task-ids $(STRICT_CHALLENGE_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-strict-challenge \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_strict_challenge \
		$(HOSTED_RESUME)

report-hosted-strict-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-strict-challenge/results.jsonl \
		--out experiments/results/hosted-strict-challenge/report.md

audit-hosted-strict-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-strict-challenge/results.jsonl \
		--pages $(CHALLENGE_PAGES) \
		--out experiments/results/hosted-strict-challenge/audit-queue.md

compare-hosted-strict-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli compare \
		--local experiments/results/strict-challenge-local/results.jsonl \
		--hosted experiments/results/hosted-strict-challenge/results.jsonl \
		--out experiments/results/hosted-strict-challenge/comparison.md

stats-hosted-strict-challenge:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-strict-challenge/results.jsonl \
		--out experiments/results/hosted-strict-challenge/stats.md

hosted-strict-challenge-refresh: strict-challenge-refresh run-hosted-strict-challenge report-hosted-strict-challenge audit-hosted-strict-challenge compare-hosted-strict-challenge stats-hosted-strict-challenge

run-hosted-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(BOUNDARY_TASKS) \
		--pages $(BOUNDARY_PAGES) \
		--conditions $(BOUNDARY_CONDITIONS) \
		--task-ids $(BOUNDARY_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-boundary \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_boundary \
		$(HOSTED_RESUME)

report-hosted-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-boundary/results.jsonl \
		--out experiments/results/hosted-boundary/report.md

audit-hosted-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-boundary/results.jsonl \
		--pages $(BOUNDARY_PAGES) \
		--out experiments/results/hosted-boundary/audit-queue.md

compare-hosted-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli compare \
		--local experiments/results/boundary-local/results.jsonl \
		--hosted experiments/results/hosted-boundary/results.jsonl \
		--out experiments/results/hosted-boundary/comparison.md

stats-hosted-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-boundary/results.jsonl \
		--out experiments/results/hosted-boundary/stats.md

hosted-boundary-refresh: boundary-refresh run-hosted-boundary report-hosted-boundary audit-hosted-boundary compare-hosted-boundary stats-hosted-boundary

run-hosted-relation-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(BOUNDARY_TASKS) \
		--pages $(BOUNDARY_PAGES) \
		--conditions $(RELATION_BOUNDARY_CONDITIONS) \
		--task-ids $(RELATION_BOUNDARY_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-relation-boundary \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_relation_boundary \
		$(HOSTED_RESUME)

report-hosted-relation-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-relation-boundary/results.jsonl \
		--out experiments/results/hosted-relation-boundary/report.md

audit-hosted-relation-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-relation-boundary/results.jsonl \
		--pages $(BOUNDARY_PAGES) \
		--out experiments/results/hosted-relation-boundary/audit-queue.md

compare-hosted-relation-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli compare \
		--local experiments/results/relation-boundary-local/results.jsonl \
		--hosted experiments/results/hosted-relation-boundary/results.jsonl \
		--out experiments/results/hosted-relation-boundary/comparison.md

stats-hosted-relation-boundary:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-relation-boundary/results.jsonl \
		--out experiments/results/hosted-relation-boundary/stats.md

hosted-relation-boundary-refresh: relation-boundary-refresh run-hosted-relation-boundary report-hosted-relation-boundary audit-hosted-relation-boundary compare-hosted-relation-boundary stats-hosted-relation-boundary

run-hosted-relation-boundary-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(BOUNDARY_TASKS) \
		--pages $(BOUNDARY_PAGES) \
		--conditions $(RELATION_BOUNDARY_CONDITIONS) \
		--task-ids $(RELATION_BOUNDARY_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-relation-boundary-repeats \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_relation_boundary_repeats \
		--repeats $(RELATION_BOUNDARY_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-relation-boundary-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-relation-boundary-repeats/results.jsonl \
		--out experiments/results/hosted-relation-boundary-repeats/report.md

audit-hosted-relation-boundary-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-relation-boundary-repeats/results.jsonl \
		--pages $(BOUNDARY_PAGES) \
		--out experiments/results/hosted-relation-boundary-repeats/audit-queue.md

stats-hosted-relation-boundary-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-relation-boundary-repeats/results.jsonl \
		--out experiments/results/hosted-relation-boundary-repeats/stats.md

hosted-relation-boundary-repeats-refresh: run-hosted-relation-boundary-repeats report-hosted-relation-boundary-repeats audit-hosted-relation-boundary-repeats stats-hosted-relation-boundary-repeats

run-hosted-relation-gate-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(BOUNDARY_TASKS) \
		--pages $(BOUNDARY_PAGES) \
		--conditions $(RELATION_GATE_CONDITIONS) \
		--task-ids $(RELATION_BOUNDARY_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-relation-gate-repeats \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_relation_gate_repeats \
		--repeats $(RELATION_GATE_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-relation-gate-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-relation-gate-repeats/results.jsonl \
		--out experiments/results/hosted-relation-gate-repeats/report.md

audit-hosted-relation-gate-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-relation-gate-repeats/results.jsonl \
		--pages $(BOUNDARY_PAGES) \
		--out experiments/results/hosted-relation-gate-repeats/audit-queue.md

stats-hosted-relation-gate-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-relation-gate-repeats/results.jsonl \
		--out experiments/results/hosted-relation-gate-repeats/stats.md

hosted-relation-gate-repeats-refresh: relation-gate-refresh run-hosted-relation-gate-repeats report-hosted-relation-gate-repeats audit-hosted-relation-gate-repeats stats-hosted-relation-gate-repeats

run-hosted-relation-gate-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(BOUNDARY_EXPANDED_TASKS) \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--conditions $(RELATION_GATE_CONDITIONS) \
		--task-ids $(RELATION_BOUNDARY_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-relation-gate-expanded-repeats \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_relation_gate_expanded_repeats \
		--repeats $(RELATION_GATE_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-relation-gate-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-relation-gate-expanded-repeats/results.jsonl \
		--out experiments/results/hosted-relation-gate-expanded-repeats/report.md

audit-hosted-relation-gate-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-relation-gate-expanded-repeats/results.jsonl \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--out experiments/results/hosted-relation-gate-expanded-repeats/audit-queue.md

stats-hosted-relation-gate-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-relation-gate-expanded-repeats/results.jsonl \
		--out experiments/results/hosted-relation-gate-expanded-repeats/stats.md

hosted-relation-gate-expanded-repeats-refresh: relation-gate-expanded-refresh run-hosted-relation-gate-expanded-repeats report-hosted-relation-gate-expanded-repeats audit-hosted-relation-gate-expanded-repeats stats-hosted-relation-gate-expanded-repeats

run-hosted-relation-classifier-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(BOUNDARY_EXPANDED_TASKS) \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--conditions $(RELATION_CLASSIFIER_CONDITIONS) \
		--task-ids $(RELATION_BOUNDARY_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-relation-classifier-expanded-repeats \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_relation_classifier_expanded_repeats \
		--repeats $(RELATION_GATE_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-relation-classifier-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-relation-classifier-expanded-repeats/results.jsonl \
		--out experiments/results/hosted-relation-classifier-expanded-repeats/report.md

audit-hosted-relation-classifier-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-relation-classifier-expanded-repeats/results.jsonl \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--out experiments/results/hosted-relation-classifier-expanded-repeats/audit-queue.md

stats-hosted-relation-classifier-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-relation-classifier-expanded-repeats/results.jsonl \
		--out experiments/results/hosted-relation-classifier-expanded-repeats/stats.md

hosted-relation-classifier-expanded-repeats-refresh: relation-classifier-expanded-refresh run-hosted-relation-classifier-expanded-repeats report-hosted-relation-classifier-expanded-repeats audit-hosted-relation-classifier-expanded-repeats stats-hosted-relation-classifier-expanded-repeats

run-hosted-relation-calibrated-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run-hosted \
		--tasks $(BOUNDARY_EXPANDED_TASKS) \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--conditions $(RELATION_CALIBRATED_CONDITIONS) \
		--task-ids $(RELATION_BOUNDARY_HOSTED_TASK_IDS) \
		--out-dir experiments/results/hosted-relation-calibrated-expanded-repeats \
		--delay-seconds $(HOSTED_DELAY_SECONDS) \
		--run-mode hosted_relation_calibrated_expanded_repeats \
		--repeats $(RELATION_GATE_REPEATS) \
		$(HOSTED_RESUME)

report-hosted-relation-calibrated-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/hosted-relation-calibrated-expanded-repeats/results.jsonl \
		--out experiments/results/hosted-relation-calibrated-expanded-repeats/report.md

audit-hosted-relation-calibrated-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli audit \
		--results experiments/results/hosted-relation-calibrated-expanded-repeats/results.jsonl \
		--pages $(BOUNDARY_EXPANDED_PAGES) \
		--out experiments/results/hosted-relation-calibrated-expanded-repeats/audit-queue.md

stats-hosted-relation-calibrated-expanded-repeats:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli stats \
		--results experiments/results/hosted-relation-calibrated-expanded-repeats/results.jsonl \
		--out experiments/results/hosted-relation-calibrated-expanded-repeats/stats.md

hosted-relation-calibrated-expanded-repeats-refresh: relation-calibrated-expanded-refresh run-hosted-relation-calibrated-expanded-repeats report-hosted-relation-calibrated-expanded-repeats audit-hosted-relation-calibrated-expanded-repeats stats-hosted-relation-calibrated-expanded-repeats
