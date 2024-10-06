SERVICE_NAME = attendance-manager-email-server

.PHONY: all deps database dev build up down logs shell clean deploy reload

# ----------Development commands----------
all: dev

deps:
	@echo "Installing dependencies ..."
	poetry install

database:
	@echo "Upgrading database..."
	poetry run alembic upgrade head

start_dev_server:
	# poetry run python -m app.main
	poetry run uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload-dir . --reload

dev: deps database start_dev_server

# format:
# 	poetry run black --line-length 100 --skip-string-normalization --skip-magic-trailing-comma --target-version py310 app

# ----------Production commands (Docker)----------
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec $(SERVICE_NAME) /bin/bash

clean:
	docker compose down -v
	docker system prune -af

deploy: down build up
	@echo "Deployment complete"

reload: down up
	@echo "Application reloaded"
