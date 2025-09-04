"""
Настройки приложения
"""

import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "src" / "config"

# Создаем директории если их нет
DATA_DIR.mkdir(exist_ok=True)

# Настройки базы данных
DATABASE_CONFIG = {
    "type": "sqlite",
    "path": str(DATA_DIR / "finance.db"),
    "echo": False,  # Логирование SQL запросов
}

# Настройки приложения
APP_CONFIG = {
    "name": "AI Finance",
    "version": "0.1.0",
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "language": "ru",
    "currency": "RUB",
    "timezone": "Europe/Moscow",
    "date_format": "%d.%m.%Y",
    "datetime_format": "%d.%m.%Y %H:%M",
    "number_format": "ru_RU",
}

# Настройки экспорта
EXPORT_CONFIG = {
    "default_format": "csv",
    "csv_encoding": "utf-8",
    "pdf_font": "DejaVuSans",
    "pdf_font_size": 10,
    "excel_sheet_name": "Финансы",
}

# Настройки отчетов
REPORT_CONFIG = {
    "default_period": "month",
    "chart_style": "seaborn",
    "chart_size": (12, 8),
    "colors": {
        "income": "#2ecc71",
        "expense": "#e74c3c",
        "balance": "#3498db",
        "budget": "#f39c12",
    }
}

# Настройки уведомлений
NOTIFICATION_CONFIG = {
    "enabled": True,
    "budget_alerts": True,
    "budget_threshold": 0.8,  # 80% от бюджета
    "low_balance_alerts": True,
    "low_balance_threshold": 1000,  # рублей
}

# Настройки резервного копирования
BACKUP_CONFIG = {
    "enabled": True,
    "auto_backup": True,
    "backup_interval": "daily",
    "max_backups": 30,
    "backup_dir": str(DATA_DIR / "backups"),
}

# Категории по умолчанию
DEFAULT_CATEGORIES = [
    # Доходы
    {"name": "Зарплата", "type": "income", "icon": "💰", "color": "#2ecc71"},
    {"name": "Фриланс", "type": "income", "icon": "💻", "color": "#2ecc71"},
    {"name": "Инвестиции", "type": "income", "icon": "📈", "color": "#2ecc71"},
    {"name": "Подарки", "type": "income", "icon": "🎁", "color": "#2ecc71"},
    
    # Расходы
    {"name": "Продукты", "type": "expense", "icon": "🛒", "color": "#e74c3c"},
    {"name": "Транспорт", "type": "expense", "icon": "🚗", "color": "#e74c3c"},
    {"name": "Развлечения", "type": "expense", "icon": "🎬", "color": "#e74c3c"},
    {"name": "Здоровье", "type": "expense", "icon": "🏥", "color": "#e74c3c"},
    {"name": "Образование", "type": "expense", "icon": "📚", "color": "#e74c3c"},
    {"name": "Коммунальные", "type": "expense", "icon": "🏠", "color": "#e74c3c"},
    {"name": "Одежда", "type": "expense", "icon": "👕", "color": "#e74c3c"},
    {"name": "Прочее", "type": "expense", "icon": "📦", "color": "#e74c3c"},
]

# Загружаем пользовательские настройки если есть
USER_CONFIG_FILE = CONFIG_DIR / "user_config.yaml"
if USER_CONFIG_FILE.exists():
    with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
        USER_CONFIG = yaml.safe_load(f)
else:
    USER_CONFIG = {}


def get_setting(key: str, default: Any = None) -> Any:
    """Получить настройку по ключу"""
    keys = key.split('.')
    value = USER_CONFIG
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def update_setting(key: str, value: Any) -> None:
    """Обновить настройку"""
    keys = key.split('.')
    config = USER_CONFIG
    
    for k in keys[:-1]:
        if k not in config:
            config[k] = {}
        config = config[k]
    
    config[keys[-1]] = value
    
    # Сохраняем в файл
    with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(USER_CONFIG, f, default_flow_style=False, allow_unicode=True)


def get_database_url() -> str:
    """Получить URL базы данных"""
    if DATABASE_CONFIG["type"] == "sqlite":
        return f"sqlite:///{DATABASE_CONFIG['path']}"
    elif DATABASE_CONFIG["type"] == "postgresql":
        return f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    else:
        raise ValueError(f"Неподдерживаемый тип базы данных: {DATABASE_CONFIG['type']}")


class Settings:
    """Класс настроек приложения"""
    
    def __init__(self):
        self.database_path = DATABASE_CONFIG["path"]
        self.debug = APP_CONFIG["debug"]
        self.language = APP_CONFIG["language"]
        self.currency = APP_CONFIG["currency"]
        self.timezone = APP_CONFIG["timezone"]


def get_settings() -> Settings:
    """Получить объект настроек"""
    return Settings()
