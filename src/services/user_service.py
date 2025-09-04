"""
Сервис для работы с пользователями
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from ..core.models.user import User
from ..data.database.database_manager import DatabaseManager
from ..data.database.models import UserModel


class UserService:
    """
    Сервис для управления пользователями
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация сервиса
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db = db_manager
        self.model = UserModel()
    
    def create_user(self, user: User) -> User:
        """
        Создает нового пользователя
        
        Args:
            user: Пользователь для создания
        
        Returns:
            Созданный пользователь с ID
        """
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
        
        data = self.model.to_db_dict(user)
        # Убираем ID из данных для вставки
        data.pop('id', None)
        
        query = self.model.get_insert_query()
        params = (
            data['username'],
            data['email'],
            data['full_name'],
            data['currency'],
            data['timezone'],
            data['language'],
            data['settings'],
            data['created_at'],
            data['updated_at']
        )
        
        user_id = self.db.execute_update(query, params)
        user.id = user_id
        
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Получает пользователя по ID
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Пользователь или None если не найден
        """
        query = f"{self.model.get_select_query()} WHERE id = ?"
        rows = self.db.execute_query(query, (user_id,))
        
        if rows:
            return self.model.from_db_row(dict(rows[0]))
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Получает пользователя по имени пользователя
        
        Args:
            username: Имя пользователя
        
        Returns:
            Пользователь или None если не найден
        """
        query = f"{self.model.get_select_query()} WHERE username = ?"
        rows = self.db.execute_query(query, (username,))
        
        if rows:
            return self.model.from_db_row(dict(rows[0]))
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Получает пользователя по email
        
        Args:
            email: Email пользователя
        
        Returns:
            Пользователь или None если не найден
        """
        query = f"{self.model.get_select_query()} WHERE email = ?"
        rows = self.db.execute_query(query, (email,))
        
        if rows:
            return self.model.from_db_row(dict(rows[0]))
        return None
    
    def update_user(self, user: User) -> User:
        """
        Обновляет пользователя
        
        Args:
            user: Пользователь для обновления
        
        Returns:
            Обновленный пользователь
        """
        user.updated_at = datetime.now()
        
        data = self.model.to_db_dict(user)
        query = self.model.get_update_query()
        params = (
            data['username'],
            data['email'],
            data['full_name'],
            data['currency'],
            data['timezone'],
            data['language'],
            data['settings'],
            data['updated_at'],
            data['id']
        )
        
        self.db.execute_update(query, params)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """
        Удаляет пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            True если пользователь удален успешно
        """
        query = self.model.get_delete_query()
        rows_affected = self.db.execute_update(query, (user_id,))
        return rows_affected > 0
    
    def get_users(self) -> List[User]:
        """
        Получает список всех пользователей
        
        Returns:
            Список пользователей
        """
        query = f"{self.model.get_select_query()} ORDER BY username ASC"
        rows = self.db.execute_query(query)
        
        return [self.model.from_db_row(dict(row)) for row in rows]
    
    def update_user_setting(self, user_id: int, key: str, value: Any) -> bool:
        """
        Обновляет настройку пользователя
        
        Args:
            user_id: ID пользователя
            key: Ключ настройки
            value: Значение настройки
        
        Returns:
            True если настройка обновлена успешно
        """
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.update_setting(key, value)
        self.update_user(user)
        return True
    
    def get_user_setting(self, user_id: int, key: str, default: Any = None) -> Any:
        """
        Получает настройку пользователя
        
        Args:
            user_id: ID пользователя
            key: Ключ настройки
            default: Значение по умолчанию
        
        Returns:
            Значение настройки
        """
        user = self.get_user(user_id)
        if not user:
            return default
        
        return user.get_setting(key, default)
    
    def create_default_user(self) -> User:
        """
        Создает пользователя по умолчанию
        
        Returns:
            Созданный пользователь
        """
        default_user = User(
            username="default",
            email="user@example.com",
            full_name="Пользователь по умолчанию",
            currency="RUB",
            timezone="Europe/Moscow",
            language="ru"
        )
        
        return self.create_user(default_user)
    
    def get_or_create_default_user(self) -> User:
        """
        Получает пользователя по умолчанию или создает его
        
        Returns:
            Пользователь по умолчанию
        """
        # Пытаемся найти пользователя по умолчанию
        user = self.get_user_by_username("default")
        
        if not user:
            # Если не найден, создаем нового
            user = self.create_default_user()
        
        return user
    
    def get_user_count(self) -> int:
        """
        Получает общее количество пользователей
        
        Returns:
            Количество пользователей
        """
        return self.db.get_table_count('users')
    
    def search_users(self, search_term: str) -> List[User]:
        """
        Поиск пользователей по имени или email
        
        Args:
            search_term: Поисковый запрос
        
        Returns:
            Список найденных пользователей
        """
        query = f"""
            {self.model.get_select_query()}
            WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ?
            ORDER BY username ASC
        """
        search_pattern = f"%{search_term}%"
        rows = self.db.execute_query(query, (search_pattern, search_pattern, search_pattern))
        
        return [self.model.from_db_row(dict(row)) for row in rows]
