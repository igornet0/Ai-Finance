#!/bin/bash

# Скрипт для остановки AI Finance

set -e

echo "🛑 Остановка AI Finance..."

# Останавливаем все контейнеры
docker-compose down

# Останавливаем контейнеры разработки если они запущены
docker-compose -f docker-compose.dev.yml down

echo "✅ Все сервисы остановлены!"

# Показываем статус
echo "📊 Статус контейнеров:"
docker-compose ps
