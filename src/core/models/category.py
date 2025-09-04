"""
Модель категории
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


class CategoryType(Enum):
    """Типы категорий"""
    INCOME = "income"
    EXPENSE = "expense"
    BOTH = "both"


@dataclass
class Category:
    """
    Модель категории для транзакций
    """
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    category_type: CategoryType = CategoryType.EXPENSE
    parent_id: Optional[int] = None
    color: str = "#3498db"  # Цвет по умолчанию
    icon: str = "📁"  # Иконка по умолчанию
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def is_income_category(self) -> bool:
        """Проверяет, является ли категория категорией доходов"""
        return self.category_type in [CategoryType.INCOME, CategoryType.BOTH]
    
    @property
    def is_expense_category(self) -> bool:
        """Проверяет, является ли категория категорией расходов"""
        return self.category_type in [CategoryType.EXPENSE, CategoryType.BOTH]
    
    def to_dict(self) -> dict:
        """Преобразует категорию в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_type': self.category_type.value,
            'parent_id': self.parent_id,
            'color': self.color,
            'icon': self.icon,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        """Создает категорию из словаря"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            category_type=CategoryType(data.get('category_type', 'expense')),
            parent_id=data.get('parent_id'),
            color=data.get('color', '#3498db'),
            icon=data.get('icon', '📁'),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
