.PHONY: up down test lint migrate shell logs install

up:
	docker compose up -d

down:
	docker compose down

test:
	pytest tests/ -v

test-contract:
	pytest tests/contract/ -v

lint:
	ruff check softlab/ && mypy softlab/

migrate:
	alembic upgrade head

shell:
	docker compose exec api bash

logs:
	docker compose logs -f api worker

install:
	pip install -e ".[dev]"
