# 🚀 Руководство по развертыванию AI Finance

## Обзор

AI Finance поддерживает несколько способов развертывания:
- **Docker Compose** (рекомендуется для продакшна)
- **Docker Compose для разработки**
- **Локальная разработка с Poetry**

## 🐳 Docker развертывание

### Требования
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM минимум
- 10GB свободного места

### Продакшн развертывание

```bash
# 1. Клонирование репозитория
git clone <repository-url>
cd Ai-Finance

# 2. Запуск всех сервисов
./docker/scripts/start.sh

# 3. Проверка статуса
docker-compose ps
```

### Режим разработки

```bash
# Запуск в режиме разработки
./docker/scripts/start-dev.sh

# Подключение к контейнеру для отладки
docker-compose -f docker-compose.dev.yml exec ai-finance-dev bash
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# База данных
DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_finance
POSTGRES_DB=ai_finance
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_URL=redis://redis:6379/0

# Приложение
DEBUG=false
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# Мониторинг
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=your_grafana_password
```

### SSL сертификаты

Для продакшна замените самоподписанные сертификаты:

```bash
# Поместите ваши сертификаты в:
docker/nginx/ssl/cert.pem
docker/nginx/ssl/key.pem
```

## 📊 Мониторинг

### Grafana
- URL: http://localhost:3000
- Логин: admin
- Пароль: admin (по умолчанию)

### Prometheus
- URL: http://localhost:9090
- Метрики приложения: http://localhost:8000/metrics

## 💾 Резервное копирование

### Автоматическое резервное копирование

```bash
# Создание резервной копии
./docker/scripts/backup.sh

# Настройка cron для автоматического backup
crontab -e
# Добавьте строку:
0 2 * * * /path/to/Ai-Finance/docker/scripts/backup.sh
```

### Восстановление из резервной копии

```bash
# Остановка сервисов
docker-compose down

# Восстановление базы данных
docker-compose up -d postgres
docker exec -i ai-finance-postgres psql -U postgres -d ai_finance < backups/ai_finance_backup_YYYYMMDD_HHMMSS.sql

# Запуск всех сервисов
docker-compose up -d
```

## 🔒 Безопасность

### Рекомендации для продакшна

1. **Измените пароли по умолчанию**:
   ```bash
   # В .env файле
   POSTGRES_PASSWORD=strong_password_here
   GRAFANA_ADMIN_PASSWORD=strong_password_here
   ```

2. **Настройте файрвол**:
   ```bash
   # Откройте только необходимые порты
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 22/tcp  # SSH
   ```

3. **Используйте HTTPS**:
   - Получите SSL сертификаты от Let's Encrypt
   - Замените самоподписанные сертификаты

4. **Регулярные обновления**:
   ```bash
   # Обновление образов
   docker-compose pull
   docker-compose up -d
   ```

## 🚨 Устранение неполадок

### Проблемы с запуском

```bash
# Проверка логов
docker-compose logs ai-finance
docker-compose logs postgres

# Проверка статуса контейнеров
docker-compose ps

# Перезапуск сервиса
docker-compose restart ai-finance
```

### Проблемы с базой данных

```bash
# Подключение к базе данных
docker-compose exec postgres psql -U postgres -d ai_finance

# Проверка подключений
docker-compose exec postgres pg_isready -U postgres
```

### Очистка и пересборка

```bash
# Полная очистка
./docker/scripts/clean.sh

# Пересборка образов
docker-compose build --no-cache
docker-compose up -d
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```yaml
# В docker-compose.yml
services:
  ai-finance:
    deploy:
      replicas: 3
    # ... остальная конфигурация
```

### Настройка балансировщика нагрузки

```yaml
# Добавьте в nginx.conf
upstream ai_finance_app {
    server ai-finance-1:8000;
    server ai-finance-2:8000;
    server ai-finance-3:8000;
}
```

## 🔄 CI/CD

### GitHub Actions пример

```yaml
name: Deploy AI Finance

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          docker-compose pull
          docker-compose up -d
          docker-compose exec ai-finance python manage.py migrate
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs`
2. Проверьте статус: `docker-compose ps`
3. Перезапустите сервисы: `docker-compose restart`
4. Создайте issue в репозитории

## 📋 Чек-лист развертывания

- [ ] Docker и Docker Compose установлены
- [ ] Репозиторий клонирован
- [ ] Переменные окружения настроены
- [ ] SSL сертификаты установлены (для продакшна)
- [ ] Пароли изменены с дефолтных
- [ ] Резервное копирование настроено
- [ ] Мониторинг работает
- [ ] Тесты проходят
- [ ] Приложение доступно по HTTPS
