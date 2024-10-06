SERVICE_NAME = attendance-manager-email-server

.PHONY: build up down logs shell test clean deploy

# ----------Development commands----------
all: dev

deps:
	@echo "Installing dependencies ..."
	poetry install

database:
	@echo "Upgrading database..."
	poetry run alembic upgrade head

dev:
	# poetry run python -m app.main
	poetry run uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload-dir . --reload

format:
	poetry run black --line-length 100 --skip-string-normalization --skip-magic-trailing-comma --target-version py310 app

# ----------Docker commands----------
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

# clean:
# 	docker compose down -v
# 	docker system prune -af

# deploy: down build up
# deploy: down up
# 	@echo "Deployment complete"



# reload: down up
# 	@echo "Application reloaded"
