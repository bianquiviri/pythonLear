.PHONY: dev down build test lint format seed migrate smoke

dev:
	docker compose up --build

down:
	docker compose down -v

build:
	docker compose build

test:
	cd backend && python -m pytest --cov=app --cov-report=term-missing

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint

format:
	cd backend && ruff check --fix . && ruff format .
	cd frontend && npm run lint:fix

seed:
	cd backend && python -m app.adapters.out.db.seed

migrate:
	cd backend && alembic upgrade head

smoke:
	bash .github/scripts/smoke.sh
