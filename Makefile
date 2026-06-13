PYTHON ?= python
PYTHONPATH ?= src
LOCAL_ENV = PYTHONPATH=$(PYTHONPATH)

.PHONY: help test run-local report-local research-refresh

help:
	@printf '%s\n' \
		'Targets:' \
		'  make test             Run unit tests.' \
		'  make run-local        Run the deterministic seed benchmark.' \
		'  make report-local     Generate a Markdown report from local results.' \
		'  make research-refresh Run local benchmark and report.'

test:
	$(LOCAL_ENV) $(PYTHON) -m unittest discover -s tests

run-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli run \
		--out-dir experiments/results/local

report-local:
	$(LOCAL_ENV) $(PYTHON) -m agentic_web_poisoning_lab.cli report \
		--results experiments/results/local/results.jsonl \
		--out experiments/results/local/report.md

research-refresh: run-local report-local
