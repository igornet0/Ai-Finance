"""
Сервис для работы с бюджетами
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from ..core.models.budget import Budget, BudgetPeriod
from ..core.models.transaction import TransactionType
from ..data.database.database_manager import DatabaseManager
from ..data.database.models import BudgetModel
from ..core.calculators.budget_calculator import BudgetCalculator


class BudgetService:
    """
    Сервис для управления бюджетами
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация сервиса
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db = db_manager
        self.model = BudgetModel()
        self.calculator = BudgetCalculator()
    
    def create_budget(self, budget: Budget) -> Budget:
        """
        Создает новый бюджет
        
        Args:
            budget: Бюджет для создания
        
        Returns:
            Созданный бюджет с ID
        """
        budget.created_at = datetime.now()
        budget.updated_at = datetime.now()
        
        data = self.model.to_db_dict(budget)
        # Убираем ID из данных для вставки
        data.pop('id', None)
        
        query = self.model.get_insert_query()
        params = (
            data['name'],
            data['category_id'],
            data['amount'],
            data['period'],
            data['start_date'],
            data['end_date'],
            data['is_active'],
            data['alert_threshold'],
            data['created_at'],
            data['updated_at']
        )
        
        budget_id = self.db.execute_update(query, params)
        budget.id = budget_id
        
        return budget
    
    def get_budget(self, budget_id: int) -> Optional[Budget]:
        """
        Получает бюджет по ID
        
        Args:
            budget_id: ID бюджета
        
        Returns:
            Бюджет или None если не найден
        """
        query = f"{self.model.get_select_query()} WHERE id = ?"
        rows = self.db.execute_query(query, (budget_id,))
        
        if rows:
            return self.model.from_db_row(dict(rows[0]))
        return None
    
    def update_budget(self, budget: Budget) -> Budget:
        """
        Обновляет бюджет
        
        Args:
            budget: Бюджет для обновления
        
        Returns:
            Обновленный бюджет
        """
        budget.updated_at = datetime.now()
        
        data = self.model.to_db_dict(budget)
        query = self.model.get_update_query()
        params = (
            data['name'],
            data['category_id'],
            data['amount'],
            data['period'],
            data['start_date'],
            data['end_date'],
            data['is_active'],
            data['alert_threshold'],
            data['updated_at'],
            data['id']
        )
        
        self.db.execute_update(query, params)
        return budget
    
    def delete_budget(self, budget_id: int) -> bool:
        """
        Удаляет бюджет
        
        Args:
            budget_id: ID бюджета
        
        Returns:
            True если бюджет удален успешно
        """
        query = self.model.get_delete_query()
        rows_affected = self.db.execute_update(query, (budget_id,))
        return rows_affected > 0
    
    def get_budgets(self, 
                   category_id: Optional[int] = None,
                   period: Optional[BudgetPeriod] = None,
                   is_active: Optional[bool] = None) -> List[Budget]:
        """
        Получает список бюджетов с фильтрацией
        
        Args:
            category_id: ID категории
            period: Период бюджета
            is_active: Активность бюджета
        
        Returns:
            Список бюджетов
        """
        query = self.model.get_select_query()
        conditions = []
        params = []
        
        if category_id:
            conditions.append("category_id = ?")
            params.append(category_id)
        
        if period:
            conditions.append("period = ?")
            params.append(period.value)
        
        if is_active is not None:
            conditions.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY name ASC"
        
        rows = self.db.execute_query(query, tuple(params))
        return [self.model.from_db_row(dict(row)) for row in rows]
    
    def get_active_budgets(self) -> List[Budget]:
        """
        Получает активные бюджеты
        
        Returns:
            Список активных бюджетов
        """
        return self.get_budgets(is_active=True)
    
    def get_budget_status(self, budget_id: int, 
                         end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Получает статус бюджета
        
        Args:
            budget_id: ID бюджета
            end_date: Дата окончания расчета
        
        Returns:
            Словарь со статусом бюджета
        """
        budget = self.get_budget(budget_id)
        if not budget:
            raise ValueError(f"Бюджет с ID {budget_id} не найден")
        
        # Получаем транзакции для расчета
        transactions = self._get_transactions_for_budget(budget, end_date)
        
        # Настраиваем калькулятор
        self.calculator.budgets = [budget]
        self.calculator.transactions = transactions
        
        return self.calculator.calculate_budget_usage(budget, end_date)
    
    def get_all_budgets_status(self, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Получает статус всех активных бюджетов
        
        Args:
            end_date: Дата окончания расчета
        
        Returns:
            Список статусов бюджетов
        """
        active_budgets = self.get_active_budgets()
        if not active_budgets:
            return []
        
        # Получаем все транзакции для расчета
        all_transactions = self._get_all_transactions()
        
        # Настраиваем калькулятор
        self.calculator.budgets = active_budgets
        self.calculator.transactions = all_transactions
        
        return self.calculator.get_all_budgets_status(end_date)
    
    def get_budget_alerts(self, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Получает предупреждения по бюджетам
        
        Args:
            end_date: Дата окончания расчета
        
        Returns:
            Список предупреждений
        """
        active_budgets = self.get_active_budgets()
        if not active_budgets:
            return []
        
        # Получаем все транзакции для расчета
        all_transactions = self._get_all_transactions()
        
        # Настраиваем калькулятор
        self.calculator.budgets = active_budgets
        self.calculator.transactions = all_transactions
        
        return self.calculator.get_budget_alerts(end_date)
    
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
        # Получаем все транзакции
        all_transactions = self._get_all_transactions()
        
        # Настраиваем калькулятор
        self.calculator.transactions = all_transactions
        
        return self.calculator.suggest_budget_amount(category_id, period, historical_months)
    
    def create_monthly_budget(self, name: str, category_id: int, 
                            amount: Decimal, year: int, month: int) -> Budget:
        """
        Создает месячный бюджет
        
        Args:
            name: Название бюджета
            category_id: ID категории
            amount: Сумма бюджета
            year: Год
            month: Месяц
        
        Returns:
            Созданный бюджет
        """
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        budget = Budget(
            name=name,
            category_id=category_id,
            amount=amount,
            period=BudgetPeriod.MONTHLY,
            start_date=start_date,
            end_date=end_date
        )
        
        return self.create_budget(budget)
    
    def create_yearly_budget(self, name: str, category_id: int, 
                           amount: Decimal, year: int) -> Budget:
        """
        Создает годовой бюджет
        
        Args:
            name: Название бюджета
            category_id: ID категории
            amount: Сумма бюджета
            year: Год
        
        Returns:
            Созданный бюджет
        """
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        budget = Budget(
            name=name,
            category_id=category_id,
            amount=amount,
            period=BudgetPeriod.YEARLY,
            start_date=start_date,
            end_date=end_date
        )
        
        return self.create_budget(budget)
    
    def get_budget_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Получает сводку по бюджетам за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Словарь со сводкой
        """
        # Получаем бюджеты, которые пересекаются с периодом
        query = f"""
            {self.model.get_select_query()}
            WHERE is_active = 1
            AND (
                (start_date <= ? AND (end_date IS NULL OR end_date >= ?))
                OR (start_date <= ? AND (end_date IS NULL OR end_date >= ?))
            )
        """
        rows = self.db.execute_query(query, (
            start_date.isoformat(), start_date.isoformat(),
            end_date.isoformat(), end_date.isoformat()
        ))
        
        budgets = [self.model.from_db_row(dict(row)) for row in rows]
        
        if not budgets:
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'total_budgets': 0,
                'total_budget_amount': 0.0,
                'budgets': []
            }
        
        # Получаем все транзакции для расчета
        all_transactions = self._get_all_transactions()
        
        # Настраиваем калькулятор
        self.calculator.budgets = budgets
        self.calculator.transactions = all_transactions
        
        # Рассчитываем статус для каждого бюджета
        budget_statuses = []
        total_budget_amount = Decimal('0.00')
        
        for budget in budgets:
            status = self.calculator.calculate_budget_usage(budget, end_date)
            budget_statuses.append(status)
            total_budget_amount += budget.amount
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_budgets': len(budgets),
            'total_budget_amount': float(total_budget_amount),
            'budgets': budget_statuses
        }
    
    def _get_transactions_for_budget(self, budget: Budget, 
                                   end_date: Optional[date] = None) -> List:
        """
        Получает транзакции для расчета бюджета
        
        Args:
            budget: Бюджет
            end_date: Дата окончания
        
        Returns:
            Список транзакций
        """
        if end_date is None:
            end_date = date.today()
        
        # Определяем период для расчета
        if budget.period == BudgetPeriod.MONTHLY:
            period_start = end_date.replace(day=1)
            if end_date.month == 12:
                period_end = end_date.replace(year=end_date.year + 1, month=1, day=1)
            else:
                period_end = end_date.replace(month=end_date.month + 1, day=1)
        elif budget.period == BudgetPeriod.YEARLY:
            period_start = end_date.replace(month=1, day=1)
            period_end = end_date.replace(month=12, day=31)
        else:
            # Для других периодов используем даты бюджета
            period_start = budget.start_date
            period_end = budget.end_date or end_date
        
        # Получаем транзакции
        query = """
            SELECT id, amount, transaction_type, category_id, description,
                   date, account_id, tags, created_at, updated_at
            FROM transactions
            WHERE transaction_type = 'expense'
            AND date >= ? AND date <= ?
        """
        
        params = [period_start.isoformat(), period_end.isoformat()]
        
        # Если бюджет привязан к категории, фильтруем по ней
        if budget.category_id:
            query += " AND category_id = ?"
            params.append(budget.category_id)
        
        rows = self.db.execute_query(query, tuple(params))
        
        # Преобразуем в объекты Transaction
        from ..data.database.models import TransactionModel
        transaction_model = TransactionModel()
        
        return [transaction_model.from_db_row(dict(row)) for row in rows]
    
    def _get_all_transactions(self) -> List:
        """
        Получает все транзакции
        
        Returns:
            Список всех транзакций
        """
        query = """
            SELECT id, amount, transaction_type, category_id, description,
                   date, account_id, tags, created_at, updated_at
            FROM transactions
            WHERE transaction_type = 'expense'
            ORDER BY date DESC
        """
        
        rows = self.db.execute_query(query)
        
        # Преобразуем в объекты Transaction
        from ..data.database.models import TransactionModel
        transaction_model = TransactionModel()
        
        return [transaction_model.from_db_row(dict(row)) for row in rows]
    
    def get_budget_count(self) -> int:
        """
        Получает общее количество бюджетов
        
        Returns:
            Количество бюджетов
        """
        return self.db.get_table_count('budgets')
