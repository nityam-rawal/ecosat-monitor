# Makefile for EcoSat Monitor

.PHONY: help build up down logs clean migrate test lint format

help:
	@echo "EcoSat Monitor - Available Commands"
	@echo "===================================="
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View service logs"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make migrate        - Run database migrations"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Lint code"
	@echo "  make format         - Format code"
	@echo "  make shell-backend  - Open backend shell"
	@echo "  make shell-frontend - Open frontend shell"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Access at:"
	@echo "  Frontend:  http://localhost:5173"
	@echo "  Backend:   http://localhost:8000"
	@echo "  Docs:      http://localhost:8000/api/v1/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +

migrate:
	docker-compose exec backend alembic upgrade head

test:
	docker-compose exec backend pytest tests/ -v
	docker-compose exec frontend npm run test

lint:
	docker-compose exec backend black app/ --check
	docker-compose exec backend ruff check app/
	docker-compose exec frontend npm run lint

format:
	docker-compose exec backend black app/
	docker-compose exec backend ruff check app/ --fix
	docker-compose exec frontend npm run format

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

psql:
	docker-compose exec db psql -U ecosat -d ecosat

redis-cli:
	docker-compose exec redis redis-cli
