"""
Модель бюджета
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class BudgetPeriod(Enum):
    """Периоды бюджета"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class Budget:
    """
    Модель бюджета
    """
    id: Optional[int] = None
    name: str = ""
    category_id: Optional[int] = None
    amount: Decimal = Decimal('0.00')
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    start_date: date = None
    end_date: Optional[date] = None
    is_active: bool = True
    alert_threshold: Decimal = Decimal('0.80')  # 80% от бюджета
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.start_date is None:
            self.start_date = date.today()
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def is_over_budget(self) -> bool:
        """Проверяет, превышен ли бюджет"""
        # Эта логика будет реализована в сервисах
        return False
    
    @property
    def is_near_limit(self) -> bool:
        """Проверяет, близок ли бюджет к лимиту"""
        # Эта логика будет реализована в сервисах
        return False
    
    def to_dict(self) -> dict:
        """Преобразует бюджет в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'amount': float(self.amount),
            'period': self.period.value,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'alert_threshold': float(self.alert_threshold),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Budget':
        """Создает бюджет из словаря"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            category_id=data.get('category_id'),
            amount=Decimal(str(data.get('amount', 0))),
            period=BudgetPeriod(data.get('period', 'monthly')),
            start_date=date.fromisoformat(data.get('start_date', date.today().isoformat())),
            end_date=date.fromisoformat(data.get('end_date')) if data.get('end_date') else None,
            is_active=data.get('is_active', True),
            alert_threshold=Decimal(str(data.get('alert_threshold', 0.8))),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
