PYTHON ?= python
PYTHONPATH ?= src
LOCAL_ENV = PYTHONPATH=$(PYTHONPATH)
HOSTED_DELAY_SECONDS ?= 8
HOSTED_RESUME ?= --resume
FOCUSED_HOSTED_CONDITIONS ?= A1_AGENT_BASELINE,A3_PROMPT_SHIELDS,A4_FULL_DEFENSE
FOCUSED_HOSTED_TASK_IDS ?= task_001,task_002,task_005,task_006,task_011,task_015,task_025,task_027
FULL_HOSTED_CONDITIONS ?= A0_DIRECT,A1_AGENT_BASELINE,A2_SOURCE_RANKING,A3_PROMPT_SHIELDS,A4_FULL_DEFENSE
FULL_HOSTED_TASK_IDS ?= all

.PHONY: help test run-local report-local audit-local research-refresh run-hosted-smoke report-hosted-smoke audit-hosted-smoke hosted-smoke-refresh run-hosted-focused report-hosted-focused audit-hosted-focused compare-hosted-focused hosted-focused-refresh run-hosted-full report-hosted-full audit-hosted-full compare-hosted-full stats-hosted-full hosted-full-refresh

help:
	@printf '%s\n' \
		'Targets:' \
		'  make test             Run unit tests.' \
		'  make run-local        Run the deterministic seed benchmark.' \
		'  make report-local     Generate a Markdown report from local results.' \
		'  make audit-local      Generate a human audit queue from local results.' \
		'  make research-refresh Run local benchmark, report, and audit queue.' \
		'  make hosted-smoke-refresh Run Azure hosted smoke, report, and audit queue.' \
		'  make hosted-focused-refresh Run focused Azure sweep, reports, and audit queue.' \
		'  make hosted-full-refresh Run full Azure matrix with comparison and stats.'

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
