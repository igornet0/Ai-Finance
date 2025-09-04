#!/bin/bash

# Скрипт для запуска AI Finance в режиме разработки

set -e

echo "🚀 Запуск AI Finance в режиме разработки..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не установлен. Установите docker-compose и попробуйте снова."
    exit 1
fi

# Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p data logs backups

# Собираем и запускаем контейнеры для разработки
echo "🔨 Сборка и запуск контейнеров для разработки..."
docker-compose -f docker-compose.dev.yml up --build -d

# Ждем запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверяем статус контейнеров
echo "📊 Статус контейнеров:"
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "🎉 AI Finance запущен в режиме разработки!"
echo ""
echo "📱 Доступные сервисы:"
echo "  🐍 Приложение: http://localhost:8000"
echo "  📓 Jupyter: http://localhost:8888"
echo "  🗄️  pgAdmin: http://localhost:5050 (admin@ai-finance.local/admin)"
echo "  🗄️  PostgreSQL: localhost:5433"
echo "  🔴 Redis: localhost:6380"
echo ""
echo "📋 Полезные команды:"
echo "  docker-compose -f docker-compose.dev.yml logs -f ai-finance-dev  # Логи приложения"
echo "  docker-compose -f docker-compose.dev.yml exec ai-finance-dev bash  # Подключение к контейнеру"
echo "  docker-compose -f docker-compose.dev.yml down  # Остановка всех сервисов"
echo "  docker-compose -f docker-compose.dev.yml restart ai-finance-dev  # Перезапуск приложения"
echo ""
echo "🔧 Для отладки:"
echo "  Приложение запущено с debugpy на порту 5678"
echo "  Подключитесь к VS Code для удаленной отладки"
