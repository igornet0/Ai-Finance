"""
Модели для работы с базой данных
"""

import json
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass

from ...core.models.transaction import Transaction, TransactionType
from ...core.models.category import Category, CategoryType
from ...core.models.budget import Budget, BudgetPeriod
from ...core.models.user import User


@dataclass
class TransactionModel:
    """Модель для работы с транзакциями в базе данных"""
    
    @staticmethod
    def to_db_dict(transaction: Transaction) -> Dict[str, Any]:
        """Преобразует Transaction в словарь для базы данных"""
        return {
            'id': transaction.id,
            'amount': float(transaction.amount),
            'transaction_type': transaction.transaction_type.value,
            'category_id': transaction.category_id,
            'description': transaction.description,
            'date': transaction.date.isoformat(),
            'account_id': transaction.account_id,
            'tags': json.dumps(transaction.tags),
            'created_at': transaction.created_at.isoformat(),
            'updated_at': transaction.updated_at.isoformat()
        }
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> Transaction:
        """Создает Transaction из строки базы данных"""
        return Transaction(
            id=row['id'],
            amount=Decimal(str(row['amount'])),
            transaction_type=TransactionType(row['transaction_type']),
            category_id=row['category_id'],
            description=row['description'] or '',
            date=datetime.fromisoformat(row['date']),
            account_id=row['account_id'],
            tags=json.loads(row['tags']) if row['tags'] else [],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    @staticmethod
    def get_insert_query() -> str:
        """Возвращает SQL запрос для вставки транзакции"""
        return """
            INSERT INTO transactions (amount, transaction_type, category_id, description, 
                                    date, account_id, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    @staticmethod
    def get_update_query() -> str:
        """Возвращает SQL запрос для обновления транзакции"""
        return """
            UPDATE transactions 
            SET amount = ?, transaction_type = ?, category_id = ?, description = ?,
                date = ?, account_id = ?, tags = ?, updated_at = ?
            WHERE id = ?
        """
    
    @staticmethod
    def get_select_query() -> str:
        """Возвращает SQL запрос для выборки транзакций"""
        return """
            SELECT id, amount, transaction_type, category_id, description,
                   date, account_id, tags, created_at, updated_at
            FROM transactions
        """
    
    @staticmethod
    def get_delete_query() -> str:
        """Возвращает SQL запрос для удаления транзакции"""
        return "DELETE FROM transactions WHERE id = ?"


@dataclass
class CategoryModel:
    """Модель для работы с категориями в базе данных"""
    
    @staticmethod
    def to_db_dict(category: Category) -> Dict[str, Any]:
        """Преобразует Category в словарь для базы данных"""
        return {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'category_type': category.category_type.value,
            'parent_id': category.parent_id,
            'color': category.color,
            'icon': category.icon,
            'is_active': category.is_active,
            'created_at': category.created_at.isoformat(),
            'updated_at': category.updated_at.isoformat()
        }
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> Category:
        """Создает Category из строки базы данных"""
        return Category(
            id=row['id'],
            name=row['name'],
            description=row['description'] or '',
            category_type=CategoryType(row['category_type']),
            parent_id=row['parent_id'],
            color=row['color'],
            icon=row['icon'],
            is_active=bool(row['is_active']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    @staticmethod
    def get_insert_query() -> str:
        """Возвращает SQL запрос для вставки категории"""
        return """
            INSERT INTO categories (name, description, category_type, parent_id,
                                  color, icon, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    @staticmethod
    def get_update_query() -> str:
        """Возвращает SQL запрос для обновления категории"""
        return """
            UPDATE categories 
            SET name = ?, description = ?, category_type = ?, parent_id = ?,
                color = ?, icon = ?, is_active = ?, updated_at = ?
            WHERE id = ?
        """
    
    @staticmethod
    def get_select_query() -> str:
        """Возвращает SQL запрос для выборки категорий"""
        return """
            SELECT id, name, description, category_type, parent_id,
                   color, icon, is_active, created_at, updated_at
            FROM categories
        """
    
    @staticmethod
    def get_delete_query() -> str:
        """Возвращает SQL запрос для удаления категории"""
        return "DELETE FROM categories WHERE id = ?"


@dataclass
class BudgetModel:
    """Модель для работы с бюджетами в базе данных"""
    
    @staticmethod
    def to_db_dict(budget: Budget) -> Dict[str, Any]:
        """Преобразует Budget в словарь для базы данных"""
        return {
            'id': budget.id,
            'name': budget.name,
            'category_id': budget.category_id,
            'amount': float(budget.amount),
            'period': budget.period.value,
            'start_date': budget.start_date.isoformat(),
            'end_date': budget.end_date.isoformat() if budget.end_date else None,
            'is_active': budget.is_active,
            'alert_threshold': float(budget.alert_threshold),
            'created_at': budget.created_at.isoformat(),
            'updated_at': budget.updated_at.isoformat()
        }
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> Budget:
        """Создает Budget из строки базы данных"""
        return Budget(
            id=row['id'],
            name=row['name'],
            category_id=row['category_id'],
            amount=Decimal(str(row['amount'])),
            period=BudgetPeriod(row['period']),
            start_date=date.fromisoformat(row['start_date']),
            end_date=date.fromisoformat(row['end_date']) if row['end_date'] else None,
            is_active=bool(row['is_active']),
            alert_threshold=Decimal(str(row['alert_threshold'])),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    @staticmethod
    def get_insert_query() -> str:
        """Возвращает SQL запрос для вставки бюджета"""
        return """
            INSERT INTO budgets (name, category_id, amount, period, start_date,
                               end_date, is_active, alert_threshold, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    @staticmethod
    def get_update_query() -> str:
        """Возвращает SQL запрос для обновления бюджета"""
        return """
            UPDATE budgets 
            SET name = ?, category_id = ?, amount = ?, period = ?, start_date = ?,
                end_date = ?, is_active = ?, alert_threshold = ?, updated_at = ?
            WHERE id = ?
        """
    
    @staticmethod
    def get_select_query() -> str:
        """Возвращает SQL запрос для выборки бюджетов"""
        return """
            SELECT id, name, category_id, amount, period, start_date,
                   end_date, is_active, alert_threshold, created_at, updated_at
            FROM budgets
        """
    
    @staticmethod
    def get_delete_query() -> str:
        """Возвращает SQL запрос для удаления бюджета"""
        return "DELETE FROM budgets WHERE id = ?"


@dataclass
class UserModel:
    """Модель для работы с пользователями в базе данных"""
    
    @staticmethod
    def to_db_dict(user: User) -> Dict[str, Any]:
        """Преобразует User в словарь для базы данных"""
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'currency': user.currency,
            'timezone': user.timezone,
            'language': user.language,
            'settings': json.dumps(user.settings),
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> User:
        """Создает User из строки базы данных"""
        return User(
            id=row['id'],
            username=row['username'],
            email=row['email'] or '',
            full_name=row['full_name'] or '',
            currency=row['currency'],
            timezone=row['timezone'],
            language=row['language'],
            settings=json.loads(row['settings']) if row['settings'] else {},
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    @staticmethod
    def get_insert_query() -> str:
        """Возвращает SQL запрос для вставки пользователя"""
        return """
            INSERT INTO users (username, email, full_name, currency, timezone,
                             language, settings, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    @staticmethod
    def get_update_query() -> str:
        """Возвращает SQL запрос для обновления пользователя"""
        return """
            UPDATE users 
            SET username = ?, email = ?, full_name = ?, currency = ?, timezone = ?,
                language = ?, settings = ?, updated_at = ?
            WHERE id = ?
        """
    
    @staticmethod
    def get_select_query() -> str:
        """Возвращает SQL запрос для выборки пользователей"""
        return """
            SELECT id, username, email, full_name, currency, timezone,
                   language, settings, created_at, updated_at
            FROM users
        """
    
    @staticmethod
    def get_delete_query() -> str:
        """Возвращает SQL запрос для удаления пользователя"""
        return "DELETE FROM users WHERE id = ?"
