#!/bin/bash

# Скрипт для запуска AI Finance в Docker

set -e

echo "🚀 Запуск AI Finance..."

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
mkdir -p docker/nginx/ssl

# Генерируем SSL сертификаты для разработки
if [ ! -f "docker/nginx/ssl/cert.pem" ]; then
    echo "🔐 Генерация SSL сертификатов..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout docker/nginx/ssl/key.pem \
        -out docker/nginx/ssl/cert.pem \
        -subj "/C=RU/ST=Moscow/L=Moscow/O=AI Finance/CN=localhost"
fi

# Собираем и запускаем контейнеры
echo "🔨 Сборка и запуск контейнеров..."
docker-compose up --build -d

# Ждем запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверяем статус контейнеров
echo "📊 Статус контейнеров:"
docker-compose ps

echo ""
echo "🎉 AI Finance запущен!"
echo ""
echo "📱 Доступные сервисы:"
echo "  🌐 Веб-интерфейс: https://localhost"
echo "  📊 Grafana: http://localhost:3000 (admin/admin)"
echo "  📈 Prometheus: http://localhost:9090"
echo "  🗄️  PostgreSQL: localhost:5432"
echo "  🔴 Redis: localhost:6379"
echo ""
echo "📋 Полезные команды:"
echo "  docker-compose logs -f ai-finance    # Логи приложения"
echo "  docker-compose exec ai-finance bash  # Подключение к контейнеру"
echo "  docker-compose down                  # Остановка всех сервисов"
echo "  docker-compose restart ai-finance    # Перезапуск приложения"
