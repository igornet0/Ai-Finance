"""
Тесты для моделей данных
"""

import pytest
from datetime import datetime, date
from decimal import Decimal

from src.core.models.transaction import Transaction, TransactionType
from src.core.models.category import Category, CategoryType
from src.core.models.budget import Budget, BudgetPeriod
from src.core.models.user import User


class TestTransaction:
    """Тесты для модели Transaction"""
    
    def test_transaction_creation(self):
        """Тест создания транзакции"""
        transaction = Transaction(
            amount=Decimal('100.50'),
            transaction_type=TransactionType.EXPENSE,
            description="Тестовая транзакция"
        )
        
        assert transaction.amount == Decimal('100.50')
        assert transaction.transaction_type == TransactionType.EXPENSE
        assert transaction.description == "Тестовая транзакция"
        assert transaction.is_expense is True
        assert transaction.is_income is False
    
    def test_transaction_type_properties(self):
        """Тест свойств типа транзакции"""
        income_transaction = Transaction(transaction_type=TransactionType.INCOME)
        expense_transaction = Transaction(transaction_type=TransactionType.EXPENSE)
        transfer_transaction = Transaction(transaction_type=TransactionType.TRANSFER)
        
        assert income_transaction.is_income is True
        assert income_transaction.is_expense is False
        
        assert expense_transaction.is_expense is True
        assert expense_transaction.is_income is False
        
        assert transfer_transaction.is_transfer is True
        assert transfer_transaction.is_income is False
        assert transfer_transaction.is_expense is False
    
    def test_transaction_to_dict(self):
        """Тест преобразования в словарь"""
        transaction = Transaction(
            id=1,
            amount=Decimal('100.50'),
            transaction_type=TransactionType.EXPENSE,
            description="Тест"
        )
        
        data = transaction.to_dict()
        
        assert data['id'] == 1
        assert data['amount'] == 100.50
        assert data['transaction_type'] == 'expense'
        assert data['description'] == 'Тест'
    
    def test_transaction_from_dict(self):
        """Тест создания из словаря"""
        data = {
            'id': 1,
            'amount': 100.50,
            'transaction_type': 'expense',
            'description': 'Тест'
        }
        
        transaction = Transaction.from_dict(data)
        
        assert transaction.id == 1
        assert transaction.amount == Decimal('100.50')
        assert transaction.transaction_type == TransactionType.EXPENSE
        assert transaction.description == 'Тест'


class TestCategory:
    """Тесты для модели Category"""
    
    def test_category_creation(self):
        """Тест создания категории"""
        category = Category(
            name="Продукты",
            category_type=CategoryType.EXPENSE,
            description="Покупка продуктов"
        )
        
        assert category.name == "Продукты"
        assert category.category_type == CategoryType.EXPENSE
        assert category.description == "Покупка продуктов"
        assert category.is_expense_category is True
        assert category.is_income_category is False
    
    def test_category_type_properties(self):
        """Тест свойств типа категории"""
        income_category = Category(category_type=CategoryType.INCOME)
        expense_category = Category(category_type=CategoryType.EXPENSE)
        both_category = Category(category_type=CategoryType.BOTH)
        
        assert income_category.is_income_category is True
        assert income_category.is_expense_category is False
        
        assert expense_category.is_expense_category is True
        assert expense_category.is_income_category is False
        
        assert both_category.is_income_category is True
        assert both_category.is_expense_category is True


class TestBudget:
    """Тесты для модели Budget"""
    
    def test_budget_creation(self):
        """Тест создания бюджета"""
        budget = Budget(
            name="Продукты",
            amount=Decimal('5000.00'),
            period=BudgetPeriod.MONTHLY
        )
        
        assert budget.name == "Продукты"
        assert budget.amount == Decimal('5000.00')
        assert budget.period == BudgetPeriod.MONTHLY
        assert budget.is_active is True
    
    def test_budget_periods(self):
        """Тест периодов бюджета"""
        daily_budget = Budget(period=BudgetPeriod.DAILY)
        weekly_budget = Budget(period=BudgetPeriod.WEEKLY)
        monthly_budget = Budget(period=BudgetPeriod.MONTHLY)
        yearly_budget = Budget(period=BudgetPeriod.YEARLY)
        
        assert daily_budget.period == BudgetPeriod.DAILY
        assert weekly_budget.period == BudgetPeriod.WEEKLY
        assert monthly_budget.period == BudgetPeriod.MONTHLY
        assert yearly_budget.period == BudgetPeriod.YEARLY


class TestUser:
    """Тесты для модели User"""
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Тестовый Пользователь"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Тестовый Пользователь"
        assert user.currency == "RUB"
        assert user.language == "ru"
    
    def test_user_settings(self):
        """Тест настроек пользователя"""
        user = User()
        
        # Тест получения настройки
        assert user.get_setting('date_format') == '%d.%m.%Y'
        assert user.get_setting('nonexistent', 'default') == 'default'
        
        # Тест обновления настройки
        user.update_setting('theme', 'dark')
        assert user.get_setting('theme') == 'dark'
