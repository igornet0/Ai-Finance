"""
Калькулятор статистики
"""

from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from ..models.transaction import Transaction, TransactionType


class StatisticsCalculator:
    """
    Калькулятор для расчета финансовой статистики
    """
    
    def __init__(self):
        self.transactions: List[Transaction] = []
    
    def add_transactions(self, transactions: List[Transaction]) -> None:
        """Добавляет транзакции для расчета"""
        self.transactions.extend(transactions)
    
    def get_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """
        Получает месячную сводку
        
        Args:
            year: Год
            month: Месяц (1-12)
        
        Returns:
            Словарь с месячной статистикой
        """
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return self._get_period_summary(start_date, end_date)
    
    def get_yearly_summary(self, year: int) -> Dict[str, Any]:
        """
        Получает годовую сводку
        
        Args:
            year: Год
        
        Returns:
            Словарь с годовой статистикой
        """
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        return self._get_period_summary(start_date, end_date)
    
    def get_trend_analysis(self, months: int = 12) -> Dict[str, Any]:
        """
        Анализ трендов за последние месяцы
        
        Args:
            months: Количество месяцев для анализа
        
        Returns:
            Словарь с анализом трендов
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        monthly_data = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_summary = self.get_monthly_summary(current_date.year, current_date.month)
            monthly_data.append({
                'year': current_date.year,
                'month': current_date.month,
                'income': month_summary['total_income'],
                'expenses': month_summary['total_expenses'],
                'net_income': month_summary['net_income']
            })
            
            # Переходим к следующему месяцу
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Рассчитываем тренды
        income_trend = self._calculate_trend([m['income'] for m in monthly_data])
        expenses_trend = self._calculate_trend([m['expenses'] for m in monthly_data])
        net_income_trend = self._calculate_trend([m['net_income'] for m in monthly_data])
        
        return {
            'period_months': months,
            'monthly_data': monthly_data,
            'trends': {
                'income': income_trend,
                'expenses': expenses_trend,
                'net_income': net_income_trend
            },
            'average_monthly': {
                'income': sum(m['income'] for m in monthly_data) / len(monthly_data),
                'expenses': sum(m['expenses'] for m in monthly_data) / len(monthly_data),
                'net_income': sum(m['net_income'] for m in monthly_data) / len(monthly_data)
            }
        }
    
    def get_category_analysis(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Анализ по категориям за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Словарь с анализом по категориям
        """
        category_stats = defaultdict(lambda: {'income': Decimal('0.00'), 'expense': Decimal('0.00'), 'count': 0})
        
        for transaction in self.transactions:
            if not (start_date <= transaction.date.date() <= end_date):
                continue
            
            category_id = transaction.category_id or 'Без категории'
            
            if transaction.is_income:
                category_stats[category_id]['income'] += transaction.amount
            elif transaction.is_expense:
                category_stats[category_id]['expense'] += transaction.amount
            
            category_stats[category_id]['count'] += 1
        
        # Преобразуем в список и сортируем по расходам
        categories_list = []
        for category_id, stats in category_stats.items():
            categories_list.append({
                'category_id': category_id,
                'income': float(stats['income']),
                'expense': float(stats['expense']),
                'net': float(stats['income'] - stats['expense']),
                'transaction_count': stats['count']
            })
        
        categories_list.sort(key=lambda x: x['expense'], reverse=True)
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'categories': categories_list,
            'top_expense_categories': categories_list[:5],
            'total_categories': len(categories_list)
        }
    
    def get_spending_patterns(self, days: int = 30) -> Dict[str, Any]:
        """
        Анализ паттернов трат
        
        Args:
            days: Количество дней для анализа
        
        Returns:
            Словарь с анализом паттернов
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Анализ по дням недели
        weekday_stats = defaultdict(lambda: {'amount': Decimal('0.00'), 'count': 0})
        
        # Анализ по времени дня
        time_stats = defaultdict(lambda: {'amount': Decimal('0.00'), 'count': 0})
        
        # Анализ по размерам транзакций
        amount_ranges = {
            'small': (0, 1000),
            'medium': (1000, 5000),
            'large': (5000, 20000),
            'very_large': (20000, float('inf'))
        }
        amount_stats = {range_name: {'amount': Decimal('0.00'), 'count': 0} 
                       for range_name in amount_ranges}
        
        for transaction in self.transactions:
            if not (start_date <= transaction.date.date() <= end_date):
                continue
            
            if not transaction.is_expense:
                continue
            
            # Анализ по дням недели
            weekday = transaction.date.strftime('%A')
            weekday_stats[weekday]['amount'] += transaction.amount
            weekday_stats[weekday]['count'] += 1
            
            # Анализ по времени дня
            hour = transaction.date.hour
            if 6 <= hour < 12:
                time_period = 'morning'
            elif 12 <= hour < 18:
                time_period = 'afternoon'
            elif 18 <= hour < 22:
                time_period = 'evening'
            else:
                time_period = 'night'
            
            time_stats[time_period]['amount'] += transaction.amount
            time_stats[time_period]['count'] += 1
            
            # Анализ по размерам транзакций
            amount = float(transaction.amount)
            for range_name, (min_val, max_val) in amount_ranges.items():
                if min_val <= amount < max_val:
                    amount_stats[range_name]['amount'] += transaction.amount
                    amount_stats[range_name]['count'] += 1
                    break
        
        return {
            'period_days': days,
            'weekday_analysis': {
                weekday: {
                    'amount': float(stats['amount']),
                    'count': stats['count'],
                    'average': float(stats['amount'] / stats['count']) if stats['count'] > 0 else 0
                }
                for weekday, stats in weekday_stats.items()
            },
            'time_analysis': {
                time_period: {
                    'amount': float(stats['amount']),
                    'count': stats['count'],
                    'average': float(stats['amount'] / stats['count']) if stats['count'] > 0 else 0
                }
                for time_period, stats in time_stats.items()
            },
            'amount_analysis': {
                range_name: {
                    'amount': float(stats['amount']),
                    'count': stats['count'],
                    'percentage': float(stats['amount'] / sum(s['amount'] for s in amount_stats.values()) * 100) 
                                 if sum(s['amount'] for s in amount_stats.values()) > 0 else 0
                }
                for range_name, stats in amount_stats.items()
            }
        }
    
    def _get_period_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Получает сводку за период"""
        total_income = Decimal('0.00')
        total_expenses = Decimal('0.00')
        transaction_count = 0
        
        for transaction in self.transactions:
            if not (start_date <= transaction.date.date() <= end_date):
                continue
            
            if transaction.is_income:
                total_income += transaction.amount
            elif transaction.is_expense:
                total_expenses += transaction.amount
            
            transaction_count += 1
        
        net_income = total_income - total_expenses
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_income': float(net_income),
            'transaction_count': transaction_count,
            'average_transaction': float((total_income + total_expenses) / transaction_count) if transaction_count > 0 else 0
        }
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Рассчитывает тренд для списка значений"""
        if len(values) < 2:
            return {'direction': 'stable', 'percentage': 0.0, 'slope': 0.0}
        
        # Простой линейный тренд
        n = len(values)
        x = list(range(n))
        
        # Рассчитываем наклон
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            slope = 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Определяем направление тренда
        if slope > 0.05:
            direction = 'increasing'
        elif slope < -0.05:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        # Рассчитываем процентное изменение
        if values[0] != 0:
            percentage_change = ((values[-1] - values[0]) / values[0]) * 100
        else:
            percentage_change = 0.0
        
        return {
            'direction': direction,
            'percentage': percentage_change,
            'slope': slope,
            'first_value': values[0],
            'last_value': values[-1]
        }
