"""
Сервис для работы с транзакциями
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from ..core.models.transaction import Transaction, TransactionType
from ..data.database.database_manager import DatabaseManager
from ..data.database.models import TransactionModel


class TransactionService:
    """
    Сервис для управления транзакциями
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация сервиса
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db = db_manager
        self.model = TransactionModel()
    
    def create_transaction(self, transaction: Transaction) -> Transaction:
        """
        Создает новую транзакцию
        
        Args:
            transaction: Транзакция для создания
        
        Returns:
            Созданная транзакция с ID
        """
        transaction.created_at = datetime.now()
        transaction.updated_at = datetime.now()
        
        data = self.model.to_db_dict(transaction)
        # Убираем ID из данных для вставки
        data.pop('id', None)
        
        query = self.model.get_insert_query()
        params = (
            data['amount'],
            data['transaction_type'],
            data['category_id'],
            data['description'],
            data['date'],
            data['account_id'],
            data['tags'],
            data['created_at'],
            data['updated_at']
        )
        
        transaction_id = self.db.execute_update(query, params)
        transaction.id = transaction_id
        
        return transaction
    
    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """
        Получает транзакцию по ID
        
        Args:
            transaction_id: ID транзакции
        
        Returns:
            Транзакция или None если не найдена
        """
        query = f"{self.model.get_select_query()} WHERE id = ?"
        rows = self.db.execute_query(query, (transaction_id,))
        
        if rows:
            return self.model.from_db_row(dict(rows[0]))
        return None
    
    def update_transaction(self, transaction: Transaction) -> Transaction:
        """
        Обновляет транзакцию
        
        Args:
            transaction: Транзакция для обновления
        
        Returns:
            Обновленная транзакция
        """
        transaction.updated_at = datetime.now()
        
        data = self.model.to_db_dict(transaction)
        query = self.model.get_update_query()
        params = (
            data['amount'],
            data['transaction_type'],
            data['category_id'],
            data['description'],
            data['date'],
            data['account_id'],
            data['tags'],
            data['updated_at'],
            data['id']
        )
        
        self.db.execute_update(query, params)
        return transaction
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Удаляет транзакцию
        
        Args:
            transaction_id: ID транзакции
        
        Returns:
            True если транзакция удалена успешно
        """
        query = self.model.get_delete_query()
        rows_affected = self.db.execute_update(query, (transaction_id,))
        return rows_affected > 0
    
    def get_transactions(self, 
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None,
                        transaction_type: Optional[TransactionType] = None,
                        category_id: Optional[int] = None,
                        account_id: Optional[int] = None,
                        limit: Optional[int] = None,
                        offset: int = 0) -> List[Transaction]:
        """
        Получает список транзакций с фильтрацией
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            transaction_type: Тип транзакции
            category_id: ID категории
            account_id: ID счета
            limit: Максимальное количество записей
            offset: Смещение для пагинации
        
        Returns:
            Список транзакций
        """
        query = self.model.get_select_query()
        conditions = []
        params = []
        
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date.isoformat())
        
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date.isoformat())
        
        if transaction_type:
            conditions.append("transaction_type = ?")
            params.append(transaction_type.value)
        
        if category_id:
            conditions.append("category_id = ?")
            params.append(category_id)
        
        if account_id:
            conditions.append("account_id = ?")
            params.append(account_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date DESC, created_at DESC"
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        rows = self.db.execute_query(query, tuple(params))
        return [self.model.from_db_row(dict(row)) for row in rows]
    
    def get_transactions_by_category(self, category_id: int, 
                                   start_date: Optional[date] = None,
                                   end_date: Optional[date] = None) -> List[Transaction]:
        """
        Получает транзакции по категории
        
        Args:
            category_id: ID категории
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Список транзакций
        """
        return self.get_transactions(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id
        )
    
    def get_transactions_summary(self, 
                               start_date: date,
                               end_date: date,
                               group_by: str = 'category') -> Dict[str, Any]:
        """
        Получает сводку по транзакциям
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            group_by: Группировка ('category', 'type', 'date')
        
        Returns:
            Словарь со сводкой
        """
        if group_by == 'category':
            query = """
                SELECT 
                    c.name as category_name,
                    t.transaction_type,
                    COUNT(*) as count,
                    SUM(t.amount) as total_amount
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.date >= ? AND t.date <= ?
                GROUP BY t.category_id, t.transaction_type
                ORDER BY total_amount DESC
            """
        elif group_by == 'type':
            query = """
                SELECT 
                    transaction_type,
                    COUNT(*) as count,
                    SUM(amount) as total_amount
                FROM transactions
                WHERE date >= ? AND date <= ?
                GROUP BY transaction_type
                ORDER BY total_amount DESC
            """
        elif group_by == 'date':
            query = """
                SELECT 
                    DATE(date) as transaction_date,
                    transaction_type,
                    COUNT(*) as count,
                    SUM(amount) as total_amount
                FROM transactions
                WHERE date >= ? AND date <= ?
                GROUP BY DATE(date), transaction_type
                ORDER BY transaction_date DESC
            """
        else:
            raise ValueError(f"Неподдерживаемая группировка: {group_by}")
        
        rows = self.db.execute_query(query, (start_date.isoformat(), end_date.isoformat()))
        
        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'group_by': group_by,
            'data': [dict(row) for row in rows]
        }
        
        return summary
    
    def get_total_income(self, start_date: date, end_date: date) -> Decimal:
        """
        Получает общую сумму доходов за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Общая сумма доходов
        """
        query = """
            SELECT SUM(amount) as total
            FROM transactions
            WHERE transaction_type = 'income' 
            AND date >= ? AND date <= ?
        """
        rows = self.db.execute_query(query, (start_date.isoformat(), end_date.isoformat()))
        
        total = rows[0]['total'] if rows and rows[0]['total'] else 0
        return Decimal(str(total))
    
    def get_total_expenses(self, start_date: date, end_date: date) -> Decimal:
        """
        Получает общую сумму расходов за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Общая сумма расходов
        """
        query = """
            SELECT SUM(amount) as total
            FROM transactions
            WHERE transaction_type = 'expense' 
            AND date >= ? AND date <= ?
        """
        rows = self.db.execute_query(query, (start_date.isoformat(), end_date.isoformat()))
        
        total = rows[0]['total'] if rows and rows[0]['total'] else 0
        return Decimal(str(total))
    
    def get_net_income(self, start_date: date, end_date: date) -> Decimal:
        """
        Получает чистый доход (доходы - расходы) за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Чистый доход
        """
        income = self.get_total_income(start_date, end_date)
        expenses = self.get_total_expenses(start_date, end_date)
        return income - expenses
    
    def search_transactions(self, search_term: str, limit: int = 50) -> List[Transaction]:
        """
        Поиск транзакций по описанию
        
        Args:
            search_term: Поисковый запрос
            limit: Максимальное количество результатов
        
        Returns:
            Список найденных транзакций
        """
        query = f"""
            {self.model.get_select_query()}
            WHERE description LIKE ?
            ORDER BY date DESC, created_at DESC
            LIMIT ?
        """
        search_pattern = f"%{search_term}%"
        rows = self.db.execute_query(query, (search_pattern, limit))
        
        return [self.model.from_db_row(dict(row)) for row in rows]
    
    def get_transaction_count(self) -> int:
        """
        Получает общее количество транзакций
        
        Returns:
            Количество транзакций
        """
        return self.db.get_table_count('transactions')
