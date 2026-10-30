.PHONY: setup download import rebuild test ui local
setup:
	uv sync --frozen
	npm ci --prefix frontend

download:
	PYTHONPATH=backend uv run --frozen python -m app.ingest download

import:
	PYTHONPATH=backend uv run --frozen python -m app.ingest import

rebuild:
	PYTHONPATH=backend uv run --frozen python -m app.ingest rebuild

test:
	uv run --frozen ruff check backend scripts/*.py
	uv run --frozen ruff format --check backend scripts/*.py
	uv run --frozen pytest -q
	npm --prefix frontend test
	npm --prefix frontend run build

local:
	./scripts/dev.sh
