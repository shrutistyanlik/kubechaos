.PHONY: install lint format test check all

install:
	pip install -e ".[dev]"

lint:
	flake8 kubechaos/ tests/

format:
	black kubechaos/ tests/

format-check:
	black --check kubechaos/ tests/

test:
	pytest tests/ -v

check: install lint format-check test
	@echo "All checks passed!"

all: install format lint test
	@echo "Ready to push!"
