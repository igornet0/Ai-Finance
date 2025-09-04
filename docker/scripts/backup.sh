#!/bin/bash

# Скрипт для создания резервной копии

set -e

echo "💾 Создание резервной копии AI Finance..."

# Проверяем, запущены ли контейнеры
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Контейнеры не запущены. Запустите их сначала с помощью ./docker/scripts/start.sh"
    exit 1
fi

# Создаем директорию для резервных копий
mkdir -p backups

# Запускаем backup контейнер
echo "🔄 Запуск процесса резервного копирования..."
docker-compose --profile backup run --rm backup

echo "✅ Резервное копирование завершено!"
echo "📁 Резервные копии сохранены в директории ./backups/"

# Показываем список созданных файлов
echo "📋 Созданные файлы:"
ls -la backups/ | tail -n +2
