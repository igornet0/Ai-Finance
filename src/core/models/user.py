"""
Модель пользователя
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class User:
    """
    Модель пользователя
    """
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    full_name: str = ""
    currency: str = "RUB"  # Валюта по умолчанию
    timezone: str = "Europe/Moscow"  # Часовой пояс по умолчанию
    language: str = "ru"  # Язык по умолчанию
    settings: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {
                'date_format': '%d.%m.%Y',
                'number_format': 'ru_RU',
                'theme': 'light',
                'notifications': True,
                'auto_backup': True
            }
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def update_setting(self, key: str, value: Any) -> None:
        """Обновляет настройку пользователя"""
        self.settings[key] = value
        self.updated_at = datetime.now()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Получает настройку пользователя"""
        return self.settings.get(key, default)
    
    def to_dict(self) -> dict:
        """Преобразует пользователя в словарь"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'currency': self.currency,
            'timezone': self.timezone,
            'language': self.language,
            'settings': self.settings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создает пользователя из словаря"""
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            email=data.get('email', ''),
            full_name=data.get('full_name', ''),
            currency=data.get('currency', 'RUB'),
            timezone=data.get('timezone', 'Europe/Moscow'),
            language=data.get('language', 'ru'),
            settings=data.get('settings', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
