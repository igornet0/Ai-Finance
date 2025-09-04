#!/usr/bin/env python3
"""
Базовый тест функциональности AI Finance
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.database.initializer import DatabaseInitializer
from src.core.models.transaction import Transaction, TransactionType
from src.core.models.category import Category, CategoryType
from src.core.models.budget import Budget, BudgetPeriod
from src.core.calculators import BalanceCalculator, StatisticsCalculator


def test_basic_functionality():
    """Тест базовой функциональности"""
    print("🧪 Тестирование базовой функциональности AI Finance...")
    
    try:
        # Инициализация базы данных
        print("📊 Инициализация базы данных...")
        db_initializer = DatabaseInitializer()
        db_initializer.initialize_database()
        
        # Получаем сервисы
        transaction_service = db_initializer.transaction_service
        category_service = db_initializer.category_service
        budget_service = db_initializer.budget_service
        
        # Тест 1: Получение категорий
        print("📁 Тест 1: Получение категорий...")
        categories = category_service.get_categories()
        print(f"   ✅ Найдено {len(categories)} категорий")
        
        # Тест 2: Добавление транзакции
        print("💳 Тест 2: Добавление транзакции...")
        income_category = next((cat for cat in categories if cat.name == "Зарплата"), None)
        if income_category:
            transaction = Transaction(
                amount=Decimal('100000.00'),
                transaction_type=TransactionType.INCOME,
                category_id=income_category.id,
                description="Тестовая зарплата",
                date=datetime.now()
            )
            created_transaction = transaction_service.create_transaction(transaction)
            print(f"   ✅ Создана транзакция ID: {created_transaction.id}")
        
        # Тест 3: Расчет баланса
        print("💰 Тест 3: Расчет баланса...")
        balance_calculator = BalanceCalculator()
        transactions = transaction_service.get_transactions()
        balance_calculator.add_transactions(transactions)
        balance = balance_calculator.calculate_balance()
        print(f"   ✅ Текущий баланс: {balance:,.2f} ₽")
        
        # Тест 4: Статистика
        print("📊 Тест 4: Статистика...")
        statistics_calculator = StatisticsCalculator()
        statistics_calculator.add_transactions(transactions)
        today = date.today()
        month_start = today.replace(day=1)
        summary = statistics_calculator._get_period_summary(month_start, today)
        print(f"   ✅ Доходы за месяц: {summary['total_income']:,.2f} ₽")
        print(f"   ✅ Расходы за месяц: {summary['total_expenses']:,.2f} ₽")
        print(f"   ✅ Чистый доход: {summary['net_income']:,.2f} ₽")
        
        # Тест 5: Бюджеты
        print("📋 Тест 5: Бюджеты...")
        budgets_status = budget_service.get_all_budgets_status()
        print(f"   ✅ Найдено {len(budgets_status)} активных бюджетов")
        
        print("\n🎉 Все тесты прошли успешно!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
