## Makefile для AI Finance проекта (Poetry + Docker v2)

.PHONY: help install dev test lint format format-check check clean run cli shell build info update add add-dev init-pre-commit pre-commit-all \
	docker-build docker-up docker-down docker-logs docker-dev docker-dev-down docker-dev-logs docker-backup docker-clean docker-start docker-start-dev docker-stop

.DEFAULT_GOAL := help

# Параметры
POETRY ?= poetry
DC ?= docker compose
DEV_COMPOSE = -f docker-compose.dev.yml
PY ?= python
PKG ?=
PY_SRC = src tests
export PYTHONPATH ?= src

# Авто-справка. Добавляйте описания после '##'
help: ## Показать эту справку
	@echo "Доступные команды:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

# Зависимости и окружение
install: ## Установить зависимости
	$(POETRY) install

dev: ## Установить зависимости с группой dev
	$(POETRY) install --with dev

update: ## Обновить зависимости (poetry update)
	$(POETRY) update

add: ## Добавить зависимость: make add PKG=package[extras]
	@if [ -z "$(PKG)" ]; then echo "Usage: make add PKG=<package>"; exit 1; fi
	$(POETRY) add $(PKG)

add-dev: ## Добавить dev-зависимость: make add-dev PKG=package[extras]
	@if [ -z "$(PKG)" ]; then echo "Usage: make add-dev PKG=<package>"; exit 1; fi
	$(POETRY) add --group dev $(PKG)

init-pre-commit: ## Установить pre-commit хуки
	$(POETRY) run pre-commit install

pre-commit-all: ## Запустить pre-commit на всех файлах
	$(POETRY) run pre-commit run --all-files

# Качество кода и тесты
test: ## Запустить тесты с покрытием (см. pyproject.toml)
	$(POETRY) run pytest

lint: ## Запустить линтеры (flake8 + mypy)
	$(POETRY) run flake8 src/ tests/
	$(POETRY) run mypy src/

format: ## Отформатировать код (black + isort)
	$(POETRY) run black $(PY_SRC)
	$(POETRY) run isort $(PY_SRC)

format-check: ## Проверить форматирование без изменений
	$(POETRY) run black --check $(PY_SRC)
	$(POETRY) run isort -c $(PY_SRC)

check: ## Полная проверка: формат, линтеры и тесты
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test

clean: ## Очистить временные и кеш-файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

# Запуск приложения
run: ## Запустить приложение (CLI main)
	$(POETRY) run $(PY) main.py

cli: ## Запустить CLI: ai-finance
	$(POETRY) run ai-finance

shell: ## Активировать Poetry shell
	$(POETRY) shell

build: ## Собрать пакет (poetry build)
	$(POETRY) build

info: ## Информация о проекте и окружении
	$(POETRY) show
	$(POETRY) env info

# Docker (используется Docker Compose v2: `docker compose`)
docker-build: ## Собрать образы (docker compose build)
	$(DC) build

docker-up: ## Запустить основную среду (в фоне)
	$(DC) up -d

docker-down: ## Остановить и удалить контейнеры
	$(DC) down

docker-logs: ## Логи основной среды
	$(DC) logs -f

docker-dev: ## Запустить dev-среду (из docker-compose.dev.yml)
	$(DC) $(DEV_COMPOSE) up --build -d

docker-dev-down: ## Остановить dev-среду
	$(DC) $(DEV_COMPOSE) down

docker-dev-logs: ## Логи dev-среды
	$(DC) $(DEV_COMPOSE) logs -f

docker-backup: ## Выполнить backup через скрипт
	./docker/scripts/backup.sh

docker-clean: ## Очистить docker-артефакты через скрипт
	./docker/scripts/clean.sh

docker-start: ## Полный запуск через Docker (скрипт)
	./docker/scripts/start.sh

docker-start-dev: ## Полный запуск dev-среды через Docker (скрипт)
	./docker/scripts/start-dev.sh

docker-stop: ## Остановить все контейнеры (скрипт)
	./docker/scripts/stop.sh
