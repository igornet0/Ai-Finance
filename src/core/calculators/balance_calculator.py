"""
Калькулятор баланса
"""

from decimal import Decimal
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from ..models.transaction import Transaction, TransactionType


class BalanceCalculator:
    """
    Калькулятор для расчета баланса и финансовых показателей
    """
    
    def __init__(self):
        self.transactions: List[Transaction] = []
    
    def add_transactions(self, transactions: List[Transaction]) -> None:
        """Добавляет транзакции для расчета"""
        self.transactions.extend(transactions)
    
    def calculate_balance(self, account_id: Optional[int] = None, 
                         end_date: Optional[date] = None) -> Decimal:
        """
        Рассчитывает текущий баланс
        
        Args:
            account_id: ID счета (если None, то по всем счетам)
            end_date: Дата окончания расчета (если None, то текущая дата)
        
        Returns:
            Текущий баланс
        """
        if end_date is None:
            end_date = date.today()
        
        balance = Decimal('0.00')
        
        for transaction in self.transactions:
            # Фильтрация по дате
            if transaction.date.date() > end_date:
                continue
            
            # Фильтрация по счету
            if account_id is not None and transaction.account_id != account_id:
                continue
            
            # Расчет баланса
            if transaction.is_income:
                balance += transaction.amount
            elif transaction.is_expense:
                balance -= transaction.amount
            # Переводы не влияют на общий баланс
        
        return balance
    
    def calculate_income(self, start_date: date, end_date: date, 
                        category_id: Optional[int] = None) -> Decimal:
        """
        Рассчитывает доходы за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            category_id: ID категории (если None, то по всем категориям)
        
        Returns:
            Сумма доходов
        """
        total_income = Decimal('0.00')
        
        for transaction in self.transactions:
            if not transaction.is_income:
                continue
            
            if not (start_date <= transaction.date.date() <= end_date):
                continue
            
            if category_id is not None and transaction.category_id != category_id:
                continue
            
            total_income += transaction.amount
        
        return total_income
    
    def calculate_expenses(self, start_date: date, end_date: date,
                          category_id: Optional[int] = None) -> Decimal:
        """
        Рассчитывает расходы за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            category_id: ID категории (если None, то по всем категориям)
        
        Returns:
            Сумма расходов
        """
        total_expenses = Decimal('0.00')
        
        for transaction in self.transactions:
            if not transaction.is_expense:
                continue
            
            if not (start_date <= transaction.date.date() <= end_date):
                continue
            
            if category_id is not None and transaction.category_id != category_id:
                continue
            
            total_expenses += transaction.amount
        
        return total_expenses
    
    def calculate_net_income(self, start_date: date, end_date: date) -> Decimal:
        """
        Рассчитывает чистый доход (доходы - расходы) за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Чистый доход
        """
        income = self.calculate_income(start_date, end_date)
        expenses = self.calculate_expenses(start_date, end_date)
        return income - expenses
    
    def get_balance_history(self, start_date: date, end_date: date,
                           account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получает историю изменения баланса
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            account_id: ID счета
        
        Returns:
            Список словарей с датой и балансом
        """
        # Сортируем транзакции по дате
        sorted_transactions = sorted(
            [t for t in self.transactions 
             if start_date <= t.date.date() <= end_date and
             (account_id is None or t.account_id == account_id)],
            key=lambda x: x.date
        )
        
        balance_history = []
        current_balance = Decimal('0.00')
        
        for transaction in sorted_transactions:
            if transaction.is_income:
                current_balance += transaction.amount
            elif transaction.is_expense:
                current_balance -= transaction.amount
            
            balance_history.append({
                'date': transaction.date.date(),
                'balance': float(current_balance),
                'transaction_id': transaction.id,
                'amount': float(transaction.amount),
                'type': transaction.transaction_type.value
            })
        
        return balance_history
    
    def get_category_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Получает сводку по категориям за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Словарь с суммами по категориям
        """
        category_summary = {
            'income': {},
            'expense': {}
        }
        
        for transaction in self.transactions:
            if not (start_date <= transaction.date.date() <= end_date):
                continue
            
            category_id = transaction.category_id or 'Без категории'
            
            if transaction.is_income:
                if category_id not in category_summary['income']:
                    category_summary['income'][category_id] = Decimal('0.00')
                category_summary['income'][category_id] += transaction.amount
            
            elif transaction.is_expense:
                if category_id not in category_summary['expense']:
                    category_summary['expense'][category_id] = Decimal('0.00')
                category_summary['expense'][category_id] += transaction.amount
        
        # Конвертируем Decimal в float для JSON сериализации
        for category_type in category_summary:
            for category_id in category_summary[category_type]:
                category_summary[category_type][category_id] = float(
                    category_summary[category_type][category_id]
                )
        
        return category_summary
