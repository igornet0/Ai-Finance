# Makefile для AI Finance проекта

.PHONY: help install dev test lint format clean run build

# Показать справку
help:
	@echo "Доступные команды:"
	@echo "  install    - Установить зависимости"
	@echo "  dev        - Установить dev зависимости"
	@echo "  test       - Запустить тесты"
	@echo "  lint       - Проверить код линтерами"
	@echo "  format     - Форматировать код"
	@echo "  clean      - Очистить временные файлы"
	@echo "  run        - Запустить приложение"
	@echo "  build      - Собрать проект"
	@echo "  shell      - Активировать виртуальное окружение"

# Установка зависимостей
install:
	poetry install

# Установка dev зависимостей
dev:
	poetry install --with dev

# Запуск тестов
test:
	poetry run pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Проверка кода
lint:
	poetry run flake8 src/ tests/
	poetry run mypy src/

# Форматирование кода
format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

# Очистка временных файлов
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Запуск приложения
run:
	poetry run python main.py

# Запуск CLI
cli:
	poetry run ai-finance

# Активация виртуального окружения
shell:
	poetry shell

# Сборка проекта
build:
	poetry build

# Показать информацию о проекте
info:
	poetry show
	poetry env info

# Обновление зависимостей
update:
	poetry update

# Добавление новой зависимости
add:
	@read -p "Введите название пакета: " package; \
	poetry add $$package

# Добавление dev зависимости
add-dev:
	@read -p "Введите название пакета: " package; \
	poetry add --group dev $$package

# Инициализация pre-commit
init-pre-commit:
	poetry run pre-commit install

# Запуск pre-commit на всех файлах
pre-commit-all:
	poetry run pre-commit run --all-files

# Docker команды
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-dev:
	docker-compose -f docker-compose.dev.yml up --build -d

docker-dev-down:
	docker-compose -f docker-compose.dev.yml down

docker-dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

docker-backup:
	./docker/scripts/backup.sh

docker-clean:
	./docker/scripts/clean.sh

# Полный запуск через Docker
docker-start:
	./docker/scripts/start.sh

docker-start-dev:
	./docker/scripts/start-dev.sh

docker-stop:
	./docker/scripts/stop.sh
