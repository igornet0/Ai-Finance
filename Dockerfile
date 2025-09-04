# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы конфигурации Poetry
COPY pyproject.toml poetry.lock README.md ./

# Настраиваем Poetry
RUN poetry config virtualenvs.create false

# Копируем исходный код
COPY src/ ./src/
COPY main.py ./
COPY data/ ./data/

# Устанавливаем зависимости
RUN poetry install --only=main

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Открываем порт для веб-интерфейса (если будет)
EXPOSE 8000

# Команда по умолчанию - запуск GUI
CMD ["python", "main.py", "gui"]
