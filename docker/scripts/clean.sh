#!/bin/bash

# Скрипт для очистки Docker ресурсов

set -e

echo "🧹 Очистка Docker ресурсов AI Finance..."

# Останавливаем все контейнеры
echo "🛑 Остановка контейнеров..."
docker-compose down
docker-compose -f docker-compose.dev.yml down

# Удаляем контейнеры
echo "🗑️  Удаление контейнеров..."
docker-compose rm -f
docker-compose -f docker-compose.dev.yml rm -f

# Удаляем образы
echo "🖼️  Удаление образов..."
docker images | grep ai-finance | awk '{print $3}' | xargs -r docker rmi -f

# Удаляем volumes
echo "💾 Удаление volumes..."
docker volume ls | grep ai-finance | awk '{print $2}' | xargs -r docker volume rm

# Удаляем сети
echo "🌐 Удаление сетей..."
docker network ls | grep ai-finance | awk '{print $1}' | xargs -r docker network rm

# Очищаем неиспользуемые ресурсы
echo "🧽 Очистка неиспользуемых ресурсов..."
docker system prune -f

echo "✅ Очистка завершена!"
echo ""
echo "💡 Для полной очистки Docker (включая все неиспользуемые ресурсы):"
echo "   docker system prune -a -f --volumes"
