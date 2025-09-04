"""
Калькулятор бюджета
"""

from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from ..models.transaction import Transaction, TransactionType
from ..models.budget import Budget, BudgetPeriod


class BudgetCalculator:
    """
    Калькулятор для работы с бюджетами
    """
    
    def __init__(self):
        self.budgets: List[Budget] = []
        self.transactions: List[Transaction] = []
    
    def add_budgets(self, budgets: List[Budget]) -> None:
        """Добавляет бюджеты для расчета"""
        self.budgets.extend(budgets)
    
    def add_transactions(self, transactions: List[Transaction]) -> None:
        """Добавляет транзакции для расчета"""
        self.transactions.extend(transactions)
    
    def calculate_budget_usage(self, budget: Budget, 
                              end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Рассчитывает использование бюджета
        
        Args:
            budget: Бюджет для расчета
            end_date: Дата окончания расчета (если None, то текущая дата)
        
        Returns:
            Словарь с информацией об использовании бюджета
        """
        if end_date is None:
            end_date = date.today()
        
        # Определяем период для расчета
        period_start, period_end = self._get_budget_period(budget, end_date)
        
        # Рассчитываем потраченную сумму
        spent_amount = self._calculate_spent_amount(
            budget, period_start, period_end
        )
        
        # Рассчитываем процент использования
        usage_percentage = (spent_amount / budget.amount * 100) if budget.amount > 0 else 0
        
        # Определяем статус бюджета
        status = self._get_budget_status(budget, spent_amount, usage_percentage)
        
        return {
            'budget_id': budget.id,
            'budget_name': budget.name,
            'budget_amount': float(budget.amount),
            'spent_amount': float(spent_amount),
            'remaining_amount': float(budget.amount - spent_amount),
            'usage_percentage': float(usage_percentage),
            'status': status,
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'is_over_budget': spent_amount > budget.amount,
            'is_near_limit': usage_percentage >= (budget.alert_threshold * 100)
        }
    
    def get_all_budgets_status(self, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Получает статус всех активных бюджетов
        
        Args:
            end_date: Дата окончания расчета
        
        Returns:
            Список словарей со статусом бюджетов
        """
        active_budgets = [b for b in self.budgets if b.is_active]
        return [self.calculate_budget_usage(budget, end_date) for budget in active_budgets]
    
    def get_budget_alerts(self, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Получает предупреждения по бюджетам
        
        Args:
            end_date: Дата окончания расчета
        
        Returns:
            Список предупреждений
        """
        alerts = []
        budgets_status = self.get_all_budgets_status(end_date)
        
        for status in budgets_status:
            if status['is_over_budget']:
                alerts.append({
                    'type': 'over_budget',
                    'budget_name': status['budget_name'],
                    'message': f"Бюджет '{status['budget_name']}' превышен на {status['remaining_amount']:.2f} руб.",
                    'severity': 'high'
                })
            elif status['is_near_limit']:
                alerts.append({
                    'type': 'near_limit',
                    'budget_name': status['budget_name'],
                    'message': f"Бюджет '{status['budget_name']}' близок к лимиту ({status['usage_percentage']:.1f}%)",
                    'severity': 'medium'
                })
        
        return alerts
    
    def suggest_budget_amount(self, category_id: int, period: BudgetPeriod,
                             historical_months: int = 3) -> Decimal:
        """
        Предлагает размер бюджета на основе исторических данных
        
        Args:
            category_id: ID категории
            period: Период бюджета
            historical_months: Количество месяцев для анализа
        
        Returns:
            Предлагаемый размер бюджета
        """
        # Получаем исторические данные
        end_date = date.today()
        start_date = end_date - timedelta(days=historical_months * 30)
        
        # Рассчитываем средние расходы по категории
        total_expenses = Decimal('0.00')
        period_count = 0
        
        current_date = start_date
        while current_date < end_date:
            period_start, period_end = self._get_period_dates(period, current_date)
            
            period_expenses = self._calculate_spent_amount_by_category(
                category_id, period_start, period_end
            )
            
            total_expenses += period_expenses
            period_count += 1
            
            # Переходим к следующему периоду
            if period == BudgetPeriod.MONTHLY:
                current_date = current_date.replace(day=1) + timedelta(days=32)
                current_date = current_date.replace(day=1)
            elif period == BudgetPeriod.WEEKLY:
                current_date += timedelta(weeks=1)
            elif period == BudgetPeriod.DAILY:
                current_date += timedelta(days=1)
            elif period == BudgetPeriod.YEARLY:
                current_date = current_date.replace(year=current_date.year + 1)
        
        # Рассчитываем среднее значение с небольшим запасом (10%)
        if period_count > 0:
            average_expenses = total_expenses / period_count
            suggested_amount = average_expenses * Decimal('1.1')  # +10% запас
            return suggested_amount
        
        return Decimal('0.00')
    
    def _get_budget_period(self, budget: Budget, end_date: date) -> tuple[date, date]:
        """Определяет период бюджета"""
        if budget.period == BudgetPeriod.MONTHLY:
            period_start = end_date.replace(day=1)
            if end_date.month == 12:
                period_end = end_date.replace(year=end_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                period_end = end_date.replace(month=end_date.month + 1, day=1) - timedelta(days=1)
        
        elif budget.period == BudgetPeriod.WEEKLY:
            # Находим начало недели (понедельник)
            days_since_monday = end_date.weekday()
            period_start = end_date - timedelta(days=days_since_monday)
            period_end = period_start + timedelta(days=6)
        
        elif budget.period == BudgetPeriod.DAILY:
            period_start = end_date
            period_end = end_date
        
        elif budget.period == BudgetPeriod.YEARLY:
            period_start = end_date.replace(month=1, day=1)
            period_end = end_date.replace(month=12, day=31)
        
        return period_start, period_end
    
    def _get_period_dates(self, period: BudgetPeriod, reference_date: date) -> tuple[date, date]:
        """Получает даты периода для заданной даты"""
        if period == BudgetPeriod.MONTHLY:
            period_start = reference_date.replace(day=1)
            if reference_date.month == 12:
                period_end = reference_date.replace(year=reference_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                period_end = reference_date.replace(month=reference_date.month + 1, day=1) - timedelta(days=1)
        
        elif period == BudgetPeriod.WEEKLY:
            days_since_monday = reference_date.weekday()
            period_start = reference_date - timedelta(days=days_since_monday)
            period_end = period_start + timedelta(days=6)
        
        elif period == BudgetPeriod.DAILY:
            period_start = reference_date
            period_end = reference_date
        
        elif period == BudgetPeriod.YEARLY:
            period_start = reference_date.replace(month=1, day=1)
            period_end = reference_date.replace(month=12, day=31)
        
        return period_start, period_end
    
    def _calculate_spent_amount(self, budget: Budget, start_date: date, end_date: date) -> Decimal:
        """Рассчитывает потраченную сумму по бюджету"""
        spent_amount = Decimal('0.00')
        
        for transaction in self.transactions:
            if not transaction.is_expense:
                continue
            
            if not (start_date <= transaction.date.date() <= end_date):
                continue
            
            # Если бюджет привязан к категории, учитываем только транзакции этой категории
            if budget.category_id is not None and transaction.category_id != budget.category_id:
                continue
            
            spent_amount += transaction.amount
        
        return spent_amount
    
    def _calculate_spent_amount_by_category(self, category_id: int, 
                                          start_date: date, end_date: date) -> Decimal:
        """Рассчитывает потраченную сумму по категории за период"""
        spent_amount = Decimal('0.00')
        
        for transaction in self.transactions:
            if not transaction.is_expense:
                continue
            
            if transaction.category_id != category_id:
                continue
            
            if not (start_date <= transaction.date.date() <= end_date):
                continue
            
            spent_amount += transaction.amount
        
        return spent_amount
    
    def _get_budget_status(self, budget: Budget, spent_amount: Decimal, 
                          usage_percentage: float) -> str:
        """Определяет статус бюджета"""
        if spent_amount > budget.amount:
            return 'over_budget'
        elif usage_percentage >= (budget.alert_threshold * 100):
            return 'near_limit'
        elif usage_percentage >= 50:
            return 'half_used'
        else:
            return 'normal'
