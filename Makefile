.PHONY: build up down logs shell test clean deploy

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec web /bin/bash

clean:
	docker compose down -v
	docker system prune -af

# deploy: down build up
deploy: down up
	@echo "Deployment complete"

dev:
	poetry run python -m app.main

# reload: down up
# 	@echo "Application reloaded"
