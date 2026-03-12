PYTHON ?= python

setup:
	uv sync

dev:
	uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

ruff-fix:
	uv run ruff check . --fix
	uv run ruff format .

mypy:
	uv run mypy .

docker-build:
	docker build -t open-ghana-id .

docker-up:
	docker compose up --build

docker-down:
	docker compose down

.PHONY: setup dev test lint format ruff-fix mypy docker-build docker-up docker-down

