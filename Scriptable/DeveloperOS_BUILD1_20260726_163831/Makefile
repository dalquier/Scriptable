.PHONY: install test lint typecheck compile demo validate

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy src/developeros

compile:
	python -m compileall -q src

demo:
	python scripts/run_demo.py

validate:
	python scripts/validate_build1.py
