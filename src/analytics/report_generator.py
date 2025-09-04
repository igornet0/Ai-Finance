"""
Генератор отчетов
"""

import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from decimal import Decimal
import os
from pathlib import Path

from ..core.models.transaction import Transaction, TransactionType
from ..core.models.category import Category
from ..core.calculators import StatisticsCalculator, BalanceCalculator
from .chart_generator import ChartGenerator


class ReportGenerator:
    """
    Генератор различных типов отчетов
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Инициализация генератора отчетов
        
        Args:
            output_dir: Директория для сохранения отчетов
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.chart_generator = ChartGenerator(str(self.output_dir / "charts"))
    
    def generate_csv_report(self, transactions: List[Transaction],
                          start_date: date, end_date: date,
                          filename: Optional[str] = None) -> str:
        """
        Генерирует CSV отчет по транзакциям
        
        Args:
            transactions: Список транзакций
            start_date: Начальная дата
            end_date: Конечная дата
            filename: Имя файла (опционально)
        
        Returns:
            Путь к сохраненному файлу
        """
        # Фильтруем транзакции по дате
        filtered_transactions = [
            t for t in transactions
            if start_date <= t.date.date() <= end_date
        ]
        
        # Подготавливаем данные для DataFrame
        data = []
        for transaction in filtered_transactions:
            data.append({
                'ID': transaction.id,
                'Дата': transaction.date.strftime('%d.%m.%Y'),
                'Время': transaction.date.strftime('%H:%M'),
                'Тип': transaction.transaction_type.value,
                'Сумма': float(transaction.amount),
                'Категория_ID': transaction.category_id,
                'Описание': transaction.description,
                'Теги': ', '.join(transaction.tags) if transaction.tags else '',
                'Создано': transaction.created_at.strftime('%d.%m.%Y %H:%M'),
                'Обновлено': transaction.updated_at.strftime('%d.%m.%Y %H:%M')
            })
        
        # Создаем DataFrame
        df = pd.DataFrame(data)
        
        # Сортируем по дате
        df = df.sort_values('Дата', ascending=False)
        
        # Генерируем имя файла
        if not filename:
            filename = f"transactions_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        
        filepath = self.output_dir / filename
        
        # Сохраняем в CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return str(filepath)
    
    def generate_summary_report(self, transactions: List[Transaction],
                              start_date: date, end_date: date,
                              filename: Optional[str] = None) -> str:
        """
        Генерирует сводный отчет
        
        Args:
            transactions: Список транзакций
            start_date: Начальная дата
            end_date: Конечная дата
            filename: Имя файла (опционально)
        
        Returns:
            Путь к сохраненному файлу
        """
        # Рассчитываем статистику
        statistics_calculator = StatisticsCalculator()
        statistics_calculator.add_transactions(transactions)
        summary = statistics_calculator._get_period_summary(start_date, end_date)
        
        # Рассчитываем баланс
        balance_calculator = BalanceCalculator()
        balance_calculator.add_transactions(transactions)
        current_balance = balance_calculator.calculate_balance()
        
        # Анализ по категориям
        category_analysis = statistics_calculator.get_category_analysis(start_date, end_date)
        
        # Создаем отчет
        report_content = f"""
ФИНАНСОВЫЙ ОТЧЕТ
================

Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}

ОБЩАЯ СТАТИСТИКА
----------------
💰 Общие доходы: {summary['total_income']:,.2f} ₽
💸 Общие расходы: {summary['total_expenses']:,.2f} ₽
📈 Чистый доход: {summary['net_income']:,.2f} ₽
💳 Текущий баланс: {current_balance:,.2f} ₽
📊 Количество транзакций: {summary['transaction_count']}
📈 Средняя транзакция: {summary['average_transaction']:,.2f} ₽

АНАЛИЗ ПО КАТЕГОРИЯМ
--------------------
"""
        
        # Добавляем топ-5 категорий расходов
        if category_analysis['top_expense_categories']:
            report_content += "\nТоп-5 категорий расходов:\n"
            for i, category in enumerate(category_analysis['top_expense_categories'][:5], 1):
                report_content += f"{i}. {category['category_id']}: {category['expense']:,.2f} ₽\n"
        
        # Анализ трендов
        if len(transactions) > 0:
            trend_data = statistics_calculator.get_trend_analysis(6)  # Последние 6 месяцев
            if trend_data['trends']:
                trends = trend_data['trends']
                report_content += f"""
АНАЛИЗ ТРЕНДОВ (последние 6 месяцев)
------------------------------------
📈 Доходы: {trends['income']['direction']} ({trends['income']['percentage']:+.1f}%)
💸 Расходы: {trends['expenses']['direction']} ({trends['expenses']['percentage']:+.1f}%)
📊 Чистый доход: {trends['net_income']['direction']} ({trends['net_income']['percentage']:+.1f}%)

СРЕДНИЕ ЗНАЧЕНИЯ ЗА МЕСЯЦ
-------------------------
💰 Средний доход: {trend_data['average_monthly']['income']:,.2f} ₽
💸 Средние расходы: {trend_data['average_monthly']['expenses']:,.2f} ₽
📈 Средний чистый доход: {trend_data['average_monthly']['net_income']:,.2f} ₽
"""
        
        # Генерируем имя файла
        if not filename:
            filename = f"summary_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.txt"
        
        filepath = self.output_dir / filename
        
        # Сохраняем отчет
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(filepath)
    
    def generate_detailed_report(self, transactions: List[Transaction],
                               categories: List[Category],
                               start_date: date, end_date: date,
                               filename: Optional[str] = None) -> str:
        """
        Генерирует детальный отчет с графиками
        
        Args:
            transactions: Список транзакций
            categories: Список категорий
            start_date: Начальная дата
            end_date: Конечная дата
            filename: Имя файла (опционально)
        
        Returns:
            Путь к сохраненному файлу
        """
        # Создаем словарь категорий для быстрого поиска
        category_dict = {cat.id: cat for cat in categories}
        
        # Рассчитываем статистику
        statistics_calculator = StatisticsCalculator()
        statistics_calculator.add_transactions(transactions)
        summary = statistics_calculator._get_period_summary(start_date, end_date)
        
        # Анализ по категориям
        category_analysis = statistics_calculator.get_category_analysis(start_date, end_date)
        
        # Создаем детальный отчет
        report_content = f"""
ДЕТАЛЬНЫЙ ФИНАНСОВЫЙ ОТЧЕТ
==========================

Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}

ОБЩАЯ СТАТИСТИКА
----------------
💰 Общие доходы: {summary['total_income']:,.2f} ₽
💸 Общие расходы: {summary['total_expenses']:,.2f} ₽
📈 Чистый доход: {summary['net_income']:,.2f} ₽
📊 Количество транзакций: {summary['transaction_count']}
📈 Средняя транзакция: {summary['average_transaction']:,.2f} ₽

ДЕТАЛЬНЫЙ АНАЛИЗ ПО КАТЕГОРИЯМ
------------------------------
"""
        
        # Добавляем детальную информацию по категориям
        for category in category_analysis['categories']:
            category_id = category['category_id']
            category_name = category_dict.get(category_id, {}).name if category_id != 'Без категории' else 'Без категории'
            
            report_content += f"""
Категория: {category_name}
  💰 Доходы: {category['income']:,.2f} ₽
  💸 Расходы: {category['expense']:,.2f} ₽
  📈 Чистый результат: {category['net']:,.2f} ₽
  📊 Количество транзакций: {category['transaction_count']}
"""
        
        # Анализ паттернов трат
        spending_patterns = statistics_calculator.get_spending_patterns(30)
        if spending_patterns:
            report_content += f"""
АНАЛИЗ ПАТТЕРНОВ ТРАТ (последние 30 дней)
-----------------------------------------

Анализ по дням недели:
"""
            for weekday, stats in spending_patterns['weekday_analysis'].items():
                report_content += f"  {weekday}: {stats['amount']:,.2f} ₽ ({stats['count']} транзакций, среднее: {stats['average']:,.2f} ₽)\n"
            
            report_content += "\nАнализ по времени дня:\n"
            for time_period, stats in spending_patterns['time_analysis'].items():
                report_content += f"  {time_period}: {stats['amount']:,.2f} ₽ ({stats['count']} транзакций, среднее: {stats['average']:,.2f} ₽)\n"
            
            report_content += "\nАнализ по размерам транзакций:\n"
            for range_name, stats in spending_patterns['amount_analysis'].items():
                report_content += f"  {range_name}: {stats['amount']:,.2f} ₽ ({stats['count']} транзакций, {stats['percentage']:.1f}% от общих расходов)\n"
        
        # Генерируем имя файла
        if not filename:
            filename = f"detailed_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.txt"
        
        filepath = self.output_dir / filename
        
        # Сохраняем отчет
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(filepath)
    
    def generate_comprehensive_report(self, transactions: List[Transaction],
                                    categories: List[Category],
                                    budget_statuses: List[Dict[str, Any]],
                                    start_date: date, end_date: date) -> Dict[str, str]:
        """
        Генерирует комплексный отчет со всеми типами отчетов и графиков
        
        Args:
            transactions: Список транзакций
            categories: Список категорий
            budget_statuses: Список статусов бюджетов
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Словарь с путями к созданным файлам
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Генерируем различные типы отчетов
        files = {}
        
        # 1. CSV отчет
        csv_file = self.generate_csv_report(
            transactions, start_date, end_date,
            f"transactions_{timestamp}.csv"
        )
        files['csv'] = csv_file
        
        # 2. Сводный отчет
        summary_file = self.generate_summary_report(
            transactions, start_date, end_date,
            f"summary_{timestamp}.txt"
        )
        files['summary'] = summary_file
        
        # 3. Детальный отчет
        detailed_file = self.generate_detailed_report(
            transactions, categories, start_date, end_date,
            f"detailed_{timestamp}.txt"
        )
        files['detailed'] = detailed_file
        
        # 4. Графики
        try:
            # История баланса
            balance_chart = self.chart_generator.generate_balance_chart(
                transactions, start_date, end_date
            )
            files['balance_chart'] = balance_chart
            
            # Доходы и расходы
            income_expense_chart = self.chart_generator.generate_income_expense_chart(
                transactions, start_date, end_date
            )
            files['income_expense_chart'] = income_expense_chart
            
            # Расходы по категориям
            category_pie_chart = self.chart_generator.generate_category_pie_chart(
                transactions, start_date, end_date
            )
            files['category_pie_chart'] = category_pie_chart
            
            # Анализ трендов
            trend_chart = self.chart_generator.generate_trend_analysis_chart(
                transactions, 12
            )
            files['trend_chart'] = trend_chart
            
            # Статус бюджетов
            if budget_statuses:
                budget_chart = self.chart_generator.generate_budget_status_chart(
                    budget_statuses
                )
                files['budget_chart'] = budget_chart
            
            # Комплексный график
            comprehensive_chart = self.chart_generator.generate_comprehensive_report(
                transactions, budget_statuses, start_date, end_date
            )
            files['comprehensive_chart'] = comprehensive_chart
            
        except Exception as e:
            print(f"Ошибка при создании графиков: {e}")
        
        return files
    
    def generate_monthly_report(self, transactions: List[Transaction],
                              categories: List[Category],
                              year: int, month: int) -> Dict[str, str]:
        """
        Генерирует месячный отчет
        
        Args:
            transactions: Список транзакций
            categories: Список категорий
            year: Год
            month: Месяц
        
        Returns:
            Словарь с путями к созданным файлам
        """
        # Определяем период
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Генерируем комплексный отчет
        return self.generate_comprehensive_report(
            transactions, categories, [], start_date, end_date
        )
    
    def generate_yearly_report(self, transactions: List[Transaction],
                             categories: List[Category],
                             year: int) -> Dict[str, str]:
        """
        Генерирует годовой отчет
        
        Args:
            transactions: Список транзакций
            categories: Список категорий
            year: Год
        
        Returns:
            Словарь с путями к созданным файлам
        """
        # Определяем период
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Генерируем комплексный отчет
        return self.generate_comprehensive_report(
            transactions, categories, [], start_date, end_date
        )
