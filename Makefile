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
BOUNDARY_CONDITIONS ?= A4_FULL_DEFENSE,A5_STRICT_ABSTENTION
BOUNDARY_HOSTED_TASK_IDS ?= all

.PHONY: help test run-local report-local audit-local research-refresh run-challenge-local report-challenge-local audit-challenge-local challenge-refresh run-strict-challenge-local report-strict-challenge-local audit-strict-challenge-local strict-challenge-refresh run-boundary-local report-boundary-local audit-boundary-local boundary-refresh run-hosted-smoke report-hosted-smoke audit-hosted-smoke hosted-smoke-refresh run-hosted-focused report-hosted-focused audit-hosted-focused compare-hosted-focused hosted-focused-refresh run-hosted-full report-hosted-full audit-hosted-full compare-hosted-full stats-hosted-full hosted-full-refresh run-hosted-challenge report-hosted-challenge audit-hosted-challenge compare-hosted-challenge stats-hosted-challenge hosted-challenge-refresh run-hosted-strict-challenge report-hosted-strict-challenge audit-hosted-strict-challenge compare-hosted-strict-challenge stats-hosted-strict-challenge hosted-strict-challenge-refresh run-hosted-boundary report-hosted-boundary audit-hosted-boundary compare-hosted-boundary stats-hosted-boundary hosted-boundary-refresh

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
		'  make hosted-smoke-refresh Run Azure hosted smoke, report, and audit queue.' \
		'  make hosted-focused-refresh Run focused Azure sweep, reports, and audit queue.' \
		'  make hosted-full-refresh Run full Azure matrix with comparison and stats.' \
		'  make hosted-challenge-refresh Run hard Azure challenge matrix with stats.' \
		'  make hosted-strict-challenge-refresh Run hard Azure challenge matrix with A5.' \
		'  make hosted-boundary-refresh Run hosted A4/A5 evidence-boundary matrix.'

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
