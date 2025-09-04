"""
Модель транзакции
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class TransactionType(Enum):
    """Типы транзакций"""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


@dataclass
class Transaction:
    """
    Модель финансовой транзакции
    """
    id: Optional[int] = None
    amount: Decimal = Decimal('0.00')
    transaction_type: TransactionType = TransactionType.EXPENSE
    category_id: Optional[int] = None
    description: str = ""
    date: datetime = None
    account_id: Optional[int] = None
    tags: list = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def is_income(self) -> bool:
        """Проверяет, является ли транзакция доходом"""
        return self.transaction_type == TransactionType.INCOME
    
    @property
    def is_expense(self) -> bool:
        """Проверяет, является ли транзакция расходом"""
        return self.transaction_type == TransactionType.EXPENSE
    
    @property
    def is_transfer(self) -> bool:
        """Проверяет, является ли транзакция переводом"""
        return self.transaction_type == TransactionType.TRANSFER
    
    def to_dict(self) -> dict:
        """Преобразует транзакцию в словарь"""
        return {
            'id': self.id,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type.value,
            'category_id': self.category_id,
            'description': self.description,
            'date': self.date.isoformat(),
            'account_id': self.account_id,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Создает транзакцию из словаря"""
        return cls(
            id=data.get('id'),
            amount=Decimal(str(data.get('amount', 0))),
            transaction_type=TransactionType(data.get('transaction_type', 'expense')),
            category_id=data.get('category_id'),
            description=data.get('description', ''),
            date=datetime.fromisoformat(data.get('date', datetime.now().isoformat())),
            account_id=data.get('account_id'),
            tags=data.get('tags', []),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
