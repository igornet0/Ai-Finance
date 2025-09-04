# Личный Финансовый Калькулятор

## Описание проекта
Личный финансовый калькулятор для управления доходами, расходами, бюджетирования и финансового планирования.

## Архитектура проекта

### Основные компоненты:

1. **Core (Ядро)**
   - `models/` - Модели данных (Transaction, Category, Budget, User)
   - `calculators/` - Движок финансовых расчетов
   - `validators/` - Валидация данных

2. **Data Layer (Слой данных)**
   - `database/` - Работа с базой данных
   - `storage/` - Файловое хранилище
   - `import_export/` - Импорт/экспорт данных

3. **Business Logic (Бизнес-логика)**
   - `services/` - Сервисы для работы с данными
   - `reports/` - Генерация отчетов
   - `analytics/` - Аналитика и статистика

4. **Presentation Layer (Презентационный слой)**
   - `ui/` - Пользовательский интерфейс
   - `cli/` - Командная строка
   - `api/` - REST API (опционально)

5. **Utilities (Утилиты)**
   - `config/` - Конфигурация
   - `utils/` - Вспомогательные функции
   - `tests/` - Тесты

## Функциональность

### Основные возможности:
- ✅ Учет доходов и расходов
- ✅ Категоризация транзакций
- ✅ Бюджетирование
- ✅ Финансовые цели
- ✅ Отчеты и аналитика
- ✅ Экспорт данных
- ✅ Импорт банковских выписок

### Типы расчетов:
- Баланс счета
- Месячный/годовой бюджет
- Накопления и инвестиции
- Кредиты и займы
- Налоговые расчеты
- Пенсионные накопления

## Технологический стек

- **Python 3.9+**
- **GUI**: tkinter (встроенный) или PyQt5/6
- **База данных**: SQLite (встроенная) или PostgreSQL
- **Аналитика**: pandas, numpy
- **Графики**: matplotlib, plotly
- **Экспорт**: reportlab (PDF), openpyxl (Excel)
- **Тестирование**: pytest

## Установка и запуск

### Требования
- Python 3.9+
- Poetry (для управления зависимостями)

### Установка Poetry
```bash
# Установка Poetry (если не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Или через pip
pip install poetry
```

### Установка проекта
```bash
# Клонирование репозитория
git clone <repository-url>
cd Ai-Finance

# Установка зависимостей через Poetry
poetry install

# Активация виртуального окружения
poetry shell

# Запуск приложения
poetry run python main.py

# Или через CLI команду
poetry run ai-finance --help
```

### Команды Poetry
```bash
# Установка зависимостей
poetry install

# Добавление новой зависимости
poetry add package-name

# Добавление dev зависимости
poetry add --group dev package-name

# Обновление зависимостей
poetry update

# Показать информацию о проекте
poetry show

# Запуск в виртуальном окружении
poetry run python script.py
```

## Структура проекта

```
Ai-Finance/
├── src/
│   ├── core/
│   │   ├── models/
│   │   ├── calculators/
│   │   └── validators/
│   ├── data/
│   │   ├── database/
│   │   ├── storage/
│   │   └── import_export/
│   ├── services/
│   ├── reports/
│   ├── analytics/
│   ├── ui/
│   ├── cli/
│   └── config/
├── tests/
├── docs/
├── data/
├── requirements.txt
├── main.py
└── README.md
```

## Текущий статус проекта

### ✅ Реализовано
- [x] Создание структуры проекта
- [x] Настройка Poetry для управления зависимостями
- [x] Базовые модели данных (Transaction, Category, Budget, User)
- [x] CLI интерфейс с основными командами
- [x] Система конфигурации
- [x] База данных SQLite с полной схемой
- [x] CRUD операции для всех сущностей
- [x] Движок финансовых расчетов (BalanceCalculator, StatisticsCalculator, BudgetCalculator)
- [x] GUI интерфейс на tkinter
- [x] Система категорий с иерархией
- [x] Бюджетирование с отслеживанием расходов
- [x] Финансовые отчеты и аналитика
- [x] Базовые тесты
- [x] Makefile для удобства разработки

### 🚧 В разработке
- [ ] Расширенная аналитика и графики
- [ ] Экспорт/импорт данных
- [ ] Система уведомлений
- [ ] Резервное копирование

### 📋 План разработки

#### Этап 1: Основа ✅ (Завершен)
- [x] Создание структуры проекта
- [x] Настройка окружения разработки (Poetry)
- [x] Базовые модели данных
- [x] Простой CLI интерфейс

#### Этап 2: Ядро ✅ (Завершен)
- [x] Движок финансовых расчетов
- [x] Система категорий
- [x] База данных SQLite
- [x] CRUD операции

#### Этап 3: Интерфейс ✅ (Завершен)
- [x] GUI интерфейс
- [x] Формы ввода данных
- [x] Таблицы и списки
- [x] Навигация

#### Этап 4: Аналитика 🚧 (В процессе)
- [x] Отчеты по периодам
- [x] Базовая статистика
- [ ] Графики и диаграммы
- [ ] Экспорт данных

#### Этап 5: Дополнительные функции (Планируется)
- [ ] Импорт банковских выписок
- [ ] Финансовые цели
- [ ] Уведомления
- [ ] Резервное копирование

## Примеры использования

### CLI команды

```bash
# Показать все доступные команды
poetry run ai-finance --help

# Добавить доход
poetry run ai-finance add-transaction --amount 50000 --category "Зарплата" --type income --description "Зарплата за декабрь"

# Добавить расход
poetry run ai-finance add-transaction --amount 5000 --category "Продукты" --type expense --description "Покупка продуктов"

# Показать текущий баланс
poetry run ai-finance balance

# Показать финансовый отчет за месяц
poetry run ai-finance report

# Показать статус бюджетов
poetry run ai-finance budget

# Показать список категорий
poetry run ai-finance categories

# Показать последние транзакции
poetry run ai-finance transactions

# Запустить графический интерфейс
poetry run ai-finance gui
```

### Основные функции

1. **Учет транзакций**: Добавление доходов и расходов с категоризацией
2. **Бюджетирование**: Создание и отслеживание бюджетов по категориям
3. **Финансовая аналитика**: Отчеты, статистика, анализ трат
4. **Управление категориями**: Создание иерархии категорий доходов и расходов
5. **CLI и GUI интерфейсы**: Удобное управление через командную строку или графический интерфейс

## Быстрый старт

### 🐳 Запуск через Docker (Рекомендуется)

```bash
# Клонирование репозитория
git clone <repository-url>
cd Ai-Finance

# Запуск в продакшн режиме
./docker/scripts/start.sh

# Или запуск в режиме разработки
./docker/scripts/start-dev.sh

# Остановка всех сервисов
./docker/scripts/stop.sh
```

### 🐍 Локальная разработка

```bash
# Клонирование и установка
git clone <repository-url>
cd Ai-Finance
poetry install

# Запуск CLI
poetry run ai-finance --help

# Добавление транзакции
poetry run ai-finance add-transaction --amount 1000 --category "Зарплата" --type income

# Запуск тестов
make test

# Форматирование кода
make format
```

## 🐳 Docker сервисы

После запуска через Docker доступны следующие сервисы:

### Продакшн режим
- **🌐 Веб-интерфейс**: https://localhost
- **📊 Grafana**: http://localhost:3000 (admin/admin)
- **📈 Prometheus**: http://localhost:9090
- **🗄️ PostgreSQL**: localhost:5432
- **🔴 Redis**: localhost:6379

### Режим разработки
- **🐍 Приложение**: http://localhost:8000
- **📓 Jupyter**: http://localhost:8888
- **🗄️ pgAdmin**: http://localhost:5050 (admin@ai-finance.local/admin)
- **🗄️ PostgreSQL**: localhost:5433
- **🔴 Redis**: localhost:6380

## 📋 Docker команды

```bash
# Основные команды
make docker-start        # Запуск в продакшн режиме
make docker-start-dev    # Запуск в режиме разработки
make docker-stop         # Остановка всех сервисов
make docker-logs         # Просмотр логов
make docker-backup       # Создание резервной копии
make docker-clean        # Очистка Docker ресурсов

# Или через скрипты
./docker/scripts/start.sh      # Запуск
./docker/scripts/start-dev.sh  # Запуск для разработки
./docker/scripts/stop.sh       # Остановка
./docker/scripts/backup.sh     # Резервное копирование
./docker/scripts/clean.sh      # Очистка
```

## Лицензия
MIT License
