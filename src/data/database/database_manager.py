"""
Менеджер базы данных
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime

from ...config.settings import get_settings


class DatabaseManager:
    """
    Менеджер для работы с базой данных SQLite
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Инициализация менеджера базы данных
        
        Args:
            db_path: Путь к файлу базы данных
        """
        if db_path is None:
            settings = get_settings()
            db_path = settings.database_path
        
        self.db_path = db_path
        self._ensure_database_directory()
        self._initialize_database()
    
    def _ensure_database_directory(self) -> None:
        """Создает директорию для базы данных если она не существует"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self) -> None:
        """Инициализирует базу данных и создает таблицы"""
        with self.get_connection() as conn:
            self._create_tables(conn)
            self._create_indexes(conn)
    
    @contextmanager
    def get_connection(self):
        """
        Контекстный менеджер для получения соединения с базой данных
        
        Yields:
            sqlite3.Connection: Соединение с базой данных
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
        try:
            yield conn
        finally:
            conn.close()
    
    def _create_tables(self, conn: sqlite3.Connection) -> None:
        """Создает таблицы в базе данных"""
        
        # Таблица пользователей
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                full_name TEXT,
                currency TEXT DEFAULT 'RUB',
                timezone TEXT DEFAULT 'Europe/Moscow',
                language TEXT DEFAULT 'ru',
                settings TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица категорий
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category_type TEXT NOT NULL CHECK (category_type IN ('income', 'expense', 'both')),
                parent_id INTEGER,
                color TEXT DEFAULT '#3498db',
                icon TEXT DEFAULT '📁',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories (id)
            )
        """)
        
        # Таблица счетов (для будущего расширения)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                account_type TEXT DEFAULT 'checking',
                balance DECIMAL(15,2) DEFAULT 0.00,
                currency TEXT DEFAULT 'RUB',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица транзакций
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount DECIMAL(15,2) NOT NULL,
                transaction_type TEXT NOT NULL CHECK (transaction_type IN ('income', 'expense', 'transfer')),
                category_id INTEGER,
                description TEXT,
                date TIMESTAMP NOT NULL,
                account_id INTEGER,
                tags TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id),
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        # Таблица бюджетов
        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                amount DECIMAL(15,2) NOT NULL,
                period TEXT NOT NULL CHECK (period IN ('daily', 'weekly', 'monthly', 'yearly')),
                start_date DATE NOT NULL,
                end_date DATE,
                is_active BOOLEAN DEFAULT 1,
                alert_threshold DECIMAL(3,2) DEFAULT 0.80,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        conn.commit()
    
    def _create_indexes(self, conn: sqlite3.Connection) -> None:
        """Создает индексы для оптимизации запросов"""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (date)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions (transaction_type)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions (category_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions (account_id)",
            "CREATE INDEX IF NOT EXISTS idx_categories_type ON categories (category_type)",
            "CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories (parent_id)",
            "CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets (category_id)",
            "CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets (period)",
            "CREATE INDEX IF NOT EXISTS idx_budgets_active ON budgets (is_active)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
        
        conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Выполняет SELECT запрос
        
        Args:
            query: SQL запрос
            params: Параметры запроса
        
        Returns:
            Список строк результата
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Выполняет INSERT/UPDATE/DELETE запрос
        
        Args:
            query: SQL запрос
            params: Параметры запроса
        
        Returns:
            ID последней вставленной строки или количество измененных строк
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid or cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Выполняет запрос для множества параметров
        
        Args:
            query: SQL запрос
            params_list: Список параметров
        
        Returns:
            Количество измененных строк
        """
        with self.get_connection() as conn:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def get_table_info(self, table_name: str) -> List[sqlite3.Row]:
        """
        Получает информацию о структуре таблицы
        
        Args:
            table_name: Имя таблицы
        
        Returns:
            Информация о колонках таблицы
        """
        return self.execute_query(f"PRAGMA table_info({table_name})")
    
    def get_table_count(self, table_name: str) -> int:
        """
        Получает количество записей в таблице
        
        Args:
            table_name: Имя таблицы
        
        Returns:
            Количество записей
        """
        result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
        return result[0]['count'] if result else 0
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Создает резервную копию базы данных
        
        Args:
            backup_path: Путь для сохранения резервной копии
        
        Returns:
            True если резервная копия создана успешно
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Ошибка при создании резервной копии: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Восстанавливает базу данных из резервной копии
        
        Args:
            backup_path: Путь к резервной копии
        
        Returns:
            True если восстановление прошло успешно
        """
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Ошибка при восстановлении базы данных: {e}")
            return False
    
    def vacuum_database(self) -> None:
        """Оптимизирует базу данных"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            conn.commit()
    
    def get_database_size(self) -> int:
        """
        Получает размер файла базы данных в байтах
        
        Returns:
            Размер файла в байтах
        """
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path)
        return 0
