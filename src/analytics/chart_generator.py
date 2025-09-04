"""
Генератор графиков и диаграмм
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import os
from pathlib import Path

from ..core.models.transaction import Transaction, TransactionType
from ..core.models.category import Category
from ..core.calculators import StatisticsCalculator, BalanceCalculator


class ChartGenerator:
    """
    Генератор графиков и диаграмм для финансовой аналитики
    """
    
    def __init__(self, output_dir: str = "charts"):
        """
        Инициализация генератора графиков
        
        Args:
            output_dir: Директория для сохранения графиков
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Настройка стиля matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Настройка шрифтов для русского языка
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_balance_chart(self, transactions: List[Transaction], 
                             start_date: date, end_date: date,
                             title: str = "История баланса") -> str:
        """
        Генерирует график истории баланса
        
        Args:
            transactions: Список транзакций
            start_date: Начальная дата
            end_date: Конечная дата
            title: Заголовок графика
        
        Returns:
            Путь к сохраненному файлу
        """
        # Рассчитываем историю баланса
        balance_calculator = BalanceCalculator()
        balance_calculator.add_transactions(transactions)
        balance_history = balance_calculator.get_balance_history(start_date, end_date)
        
        if not balance_history:
            raise ValueError("Нет данных для построения графика баланса")
        
        # Подготавливаем данные
        dates = [item['date'] for item in balance_history]
        balances = [item['balance'] for item in balance_history]
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dates, balances, linewidth=2, marker='o', markersize=4)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Баланс (₽)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Форматируем ось X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.xticks(rotation=45)
        
        # Форматируем ось Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f} ₽'))
        
        # Добавляем аннотацию с текущим балансом
        current_balance = balances[-1]
        ax.annotate(f'Текущий баланс: {current_balance:,.2f} ₽',
                   xy=(dates[-1], current_balance),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.tight_layout()
        
        # Сохраняем график
        filename = f"balance_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def generate_income_expense_chart(self, transactions: List[Transaction],
                                    start_date: date, end_date: date,
                                    title: str = "Доходы и расходы") -> str:
        """
        Генерирует график доходов и расходов
        
        Args:
            transactions: Список транзакций
            start_date: Начальная дата
            end_date: Конечная дата
            title: Заголовок графика
        
        Returns:
            Путь к сохраненному файлу
        """
        # Рассчитываем статистику
        statistics_calculator = StatisticsCalculator()
        statistics_calculator.add_transactions(transactions)
        
        # Получаем данные по месяцам
        monthly_data = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_summary = statistics_calculator.get_monthly_summary(
                current_date.year, current_date.month
            )
            monthly_data.append({
                'date': current_date,
                'income': month_summary['total_income'],
                'expenses': month_summary['total_expenses'],
                'net': month_summary['net_income']
            })
            
            # Переходим к следующему месяцу
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        if not monthly_data:
            raise ValueError("Нет данных для построения графика")
        
        # Подготавливаем данные
        dates = [item['date'] for item in monthly_data]
        incomes = [item['income'] for item in monthly_data]
        expenses = [item['expenses'] for item in monthly_data]
        net_incomes = [item['net'] for item in monthly_data]
        
        # Создаем график
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # График доходов и расходов
        width = 0.35
        x_pos = range(len(dates))
        
        ax1.bar([x - width/2 for x in x_pos], incomes, width, 
               label='Доходы', color='green', alpha=0.7)
        ax1.bar([x + width/2 for x in x_pos], expenses, width,
               label='Расходы', color='red', alpha=0.7)
        
        ax1.set_title(f"{title} по месяцам", fontsize=14, fontweight='bold')
        ax1.set_ylabel('Сумма (₽)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Форматируем ось X
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([d.strftime('%m.%Y') for d in dates], rotation=45)
        
        # Форматируем ось Y
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f} ₽'))
        
        # График чистого дохода
        colors = ['green' if x >= 0 else 'red' for x in net_incomes]
        ax2.bar(x_pos, net_incomes, color=colors, alpha=0.7)
        ax2.set_title('Чистый доход по месяцам', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Месяц', fontsize=12)
        ax2.set_ylabel('Чистый доход (₽)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Форматируем ось X
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([d.strftime('%m.%Y') for d in dates], rotation=45)
        
        # Форматируем ось Y
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f} ₽'))
        
        plt.tight_layout()
        
        # Сохраняем график
        filename = f"income_expense_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def generate_category_pie_chart(self, transactions: List[Transaction],
                                  start_date: date, end_date: date,
                                  transaction_type: TransactionType = TransactionType.EXPENSE,
                                  title: str = "Расходы по категориям") -> str:
        """
        Генерирует круговую диаграмму по категориям
        
        Args:
            transactions: Список транзакций
            start_date: Начальная дата
            end_date: Конечная дата
            transaction_type: Тип транзакций
            title: Заголовок графика
        
        Returns:
            Путь к сохраненному файлу
        """
        # Фильтруем транзакции
        filtered_transactions = [
            t for t in transactions
            if (start_date <= t.date.date() <= end_date and 
                t.transaction_type == transaction_type)
        ]
        
        if not filtered_transactions:
            raise ValueError(f"Нет {transaction_type.value} транзакций для построения графика")
        
        # Группируем по категориям
        category_totals = {}
        for transaction in filtered_transactions:
            category_name = f"Категория {transaction.category_id}" if transaction.category_id else "Без категории"
            if category_name not in category_totals:
                category_totals[category_name] = Decimal('0.00')
            category_totals[category_name] += transaction.amount
        
        # Подготавливаем данные
        labels = list(category_totals.keys())
        sizes = [float(amount) for amount in category_totals.values()]
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Создаем круговую диаграмму
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                         startangle=90, colors=plt.cm.Set3.colors)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        
        # Улучшаем читаемость
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Добавляем легенду с суммами
        legend_labels = [f"{label}: {sizes[i]:,.2f} ₽" for i, label in enumerate(labels)]
        ax.legend(wedges, legend_labels, title="Категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        
        # Сохраняем график
        filename = f"category_pie_{transaction_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def generate_trend_analysis_chart(self, transactions: List[Transaction],
                                    months: int = 12,
                                    title: str = "Анализ трендов") -> str:
        """
        Генерирует график анализа трендов
        
        Args:
            transactions: Список транзакций
            months: Количество месяцев для анализа
            title: Заголовок графика
        
        Returns:
            Путь к сохраненному файлу
        """
        # Рассчитываем тренды
        statistics_calculator = StatisticsCalculator()
        statistics_calculator.add_transactions(transactions)
        trend_data = statistics_calculator.get_trend_analysis(months)
        
        if not trend_data['monthly_data']:
            raise ValueError("Нет данных для анализа трендов")
        
        # Подготавливаем данные
        monthly_data = trend_data['monthly_data']
        dates = [f"{item['year']}-{item['month']:02d}" for item in monthly_data]
        incomes = [item['income'] for item in monthly_data]
        expenses = [item['expenses'] for item in monthly_data]
        net_incomes = [item['net_income'] for item in monthly_data]
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Строим линии трендов
        x_pos = range(len(dates))
        ax.plot(x_pos, incomes, marker='o', linewidth=2, label='Доходы', color='green')
        ax.plot(x_pos, expenses, marker='s', linewidth=2, label='Расходы', color='red')
        ax.plot(x_pos, net_incomes, marker='^', linewidth=2, label='Чистый доход', color='blue')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Месяц', fontsize=12)
        ax.set_ylabel('Сумма (₽)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Форматируем ось X
        ax.set_xticks(x_pos)
        ax.set_xticklabels(dates, rotation=45)
        
        # Форматируем ось Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f} ₽'))
        
        # Добавляем информацию о трендах
        trends = trend_data['trends']
        trend_text = f"Тренды:\n"
        trend_text += f"Доходы: {trends['income']['direction']} ({trends['income']['percentage']:+.1f}%)\n"
        trend_text += f"Расходы: {trends['expenses']['direction']} ({trends['expenses']['percentage']:+.1f}%)\n"
        trend_text += f"Чистый доход: {trends['net_income']['direction']} ({trends['net_income']['percentage']:+.1f}%)"
        
        ax.text(0.02, 0.98, trend_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # Сохраняем график
        filename = f"trend_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def generate_budget_status_chart(self, budget_statuses: List[Dict[str, Any]],
                                   title: str = "Статус бюджетов") -> str:
        """
        Генерирует график статуса бюджетов
        
        Args:
            budget_statuses: Список статусов бюджетов
            title: Заголовок графика
        
        Returns:
            Путь к сохраненному файлу
        """
        if not budget_statuses:
            raise ValueError("Нет данных о бюджетах")
        
        # Подготавливаем данные
        budget_names = [status['budget_name'] for status in budget_statuses]
        budget_amounts = [status['budget_amount'] for status in budget_statuses]
        spent_amounts = [status['spent_amount'] for status in budget_statuses]
        usage_percentages = [status['usage_percentage'] for status in budget_statuses]
        
        # Создаем график
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # График бюджетов vs потрачено
        x_pos = range(len(budget_names))
        width = 0.35
        
        ax1.bar([x - width/2 for x in x_pos], budget_amounts, width,
               label='Бюджет', color='lightblue', alpha=0.7)
        ax1.bar([x + width/2 for x in x_pos], spent_amounts, width,
               label='Потрачено', color='orange', alpha=0.7)
        
        ax1.set_title('Бюджеты vs Потрачено', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Сумма (₽)', fontsize=12)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(budget_names, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Форматируем ось Y
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f} ₽'))
        
        # График процента использования
        colors = ['red' if p > 100 else 'orange' if p > 80 else 'green' for p in usage_percentages]
        bars = ax2.bar(x_pos, usage_percentages, color=colors, alpha=0.7)
        
        ax2.set_title('Процент использования бюджетов', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Процент (%)', fontsize=12)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(budget_names, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
        
        # Добавляем линию 100%
        ax2.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='100%')
        ax2.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='80%')
        ax2.legend()
        
        # Добавляем значения на столбцы
        for bar, percentage in zip(bars, usage_percentages):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{percentage:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Сохраняем график
        filename = f"budget_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def generate_comprehensive_report(self, transactions: List[Transaction],
                                    budget_statuses: List[Dict[str, Any]],
                                    start_date: date, end_date: date) -> str:
        """
        Генерирует комплексный отчет с несколькими графиками
        
        Args:
            transactions: Список транзакций
            budget_statuses: Список статусов бюджетов
            start_date: Начальная дата
            end_date: Конечная дата
        
        Returns:
            Путь к сохраненному файлу
        """
        # Создаем комплексный график
        fig = plt.figure(figsize=(20, 16))
        
        # График 1: История баланса
        ax1 = plt.subplot(3, 2, 1)
        balance_calculator = BalanceCalculator()
        balance_calculator.add_transactions(transactions)
        balance_history = balance_calculator.get_balance_history(start_date, end_date)
        
        if balance_history:
            dates = [item['date'] for item in balance_history]
            balances = [item['balance'] for item in balance_history]
            ax1.plot(dates, balances, linewidth=2, marker='o', markersize=4)
            ax1.set_title('История баланса', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Баланс (₽)')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # График 2: Доходы и расходы
        ax2 = plt.subplot(3, 2, 2)
        statistics_calculator = StatisticsCalculator()
        statistics_calculator.add_transactions(transactions)
        
        # Получаем данные по месяцам
        monthly_data = []
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            month_summary = statistics_calculator.get_monthly_summary(
                current_date.year, current_date.month
            )
            monthly_data.append({
                'date': current_date,
                'income': month_summary['total_income'],
                'expenses': month_summary['total_expenses']
            })
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        if monthly_data:
            dates = [item['date'] for item in monthly_data]
            incomes = [item['income'] for item in monthly_data]
            expenses = [item['expenses'] for item in monthly_data]
            
            x_pos = range(len(dates))
            width = 0.35
            ax2.bar([x - width/2 for x in x_pos], incomes, width, label='Доходы', color='green', alpha=0.7)
            ax2.bar([x + width/2 for x in x_pos], expenses, width, label='Расходы', color='red', alpha=0.7)
            ax2.set_title('Доходы и расходы по месяцам', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Сумма (₽)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels([d.strftime('%m.%Y') for d in dates], rotation=45)
        
        # График 3: Расходы по категориям
        ax3 = plt.subplot(3, 2, 3)
        expense_transactions = [t for t in transactions if t.transaction_type == TransactionType.EXPENSE]
        if expense_transactions:
            category_totals = {}
            for transaction in expense_transactions:
                if start_date <= transaction.date.date() <= end_date:
                    category_name = f"Кат. {transaction.category_id}" if transaction.category_id else "Без категории"
                    if category_name not in category_totals:
                        category_totals[category_name] = Decimal('0.00')
                    category_totals[category_name] += transaction.amount
            
            if category_totals:
                labels = list(category_totals.keys())
                sizes = [float(amount) for amount in category_totals.values()]
                ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax3.set_title('Расходы по категориям', fontsize=14, fontweight='bold')
        
        # График 4: Статус бюджетов
        ax4 = plt.subplot(3, 2, 4)
        if budget_statuses:
            budget_names = [status['budget_name'] for status in budget_statuses]
            usage_percentages = [status['usage_percentage'] for status in budget_statuses]
            
            colors = ['red' if p > 100 else 'orange' if p > 80 else 'green' for p in usage_percentages]
            bars = ax4.bar(range(len(budget_names)), usage_percentages, color=colors, alpha=0.7)
            
            ax4.set_title('Использование бюджетов', fontsize=14, fontweight='bold')
            ax4.set_ylabel('Процент (%)')
            ax4.set_xticks(range(len(budget_names)))
            ax4.set_xticklabels(budget_names, rotation=45, ha='right')
            ax4.grid(True, alpha=0.3)
            ax4.axhline(y=100, color='red', linestyle='--', alpha=0.7)
            ax4.axhline(y=80, color='orange', linestyle='--', alpha=0.7)
        
        # График 5: Тренды
        ax5 = plt.subplot(3, 2, 5)
        if len(monthly_data) > 1:
            dates = [item['date'] for item in monthly_data]
            incomes = [item['income'] for item in monthly_data]
            expenses = [item['expenses'] for item in monthly_data]
            net_incomes = [incomes[i] - expenses[i] for i in range(len(incomes))]
            
            x_pos = range(len(dates))
            ax5.plot(x_pos, incomes, marker='o', linewidth=2, label='Доходы', color='green')
            ax5.plot(x_pos, expenses, marker='s', linewidth=2, label='Расходы', color='red')
            ax5.plot(x_pos, net_incomes, marker='^', linewidth=2, label='Чистый доход', color='blue')
            
            ax5.set_title('Тренды', fontsize=14, fontweight='bold')
            ax5.set_ylabel('Сумма (₽)')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            ax5.set_xticks(x_pos)
            ax5.set_xticklabels([d.strftime('%m.%Y') for d in dates], rotation=45)
        
        # График 6: Сводная информация
        ax6 = plt.subplot(3, 2, 6)
        ax6.axis('off')
        
        # Рассчитываем сводную статистику
        total_income = sum(item['income'] for item in monthly_data) if monthly_data else 0
        total_expenses = sum(item['expenses'] for item in monthly_data) if monthly_data else 0
        net_income = total_income - total_expenses
        current_balance = balances[-1] if balance_history else 0
        
        summary_text = f"""
СВОДНАЯ ИНФОРМАЦИЯ
Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}

💰 Общие доходы: {total_income:,.2f} ₽
💸 Общие расходы: {total_expenses:,.2f} ₽
📈 Чистый доход: {net_income:,.2f} ₽
💳 Текущий баланс: {current_balance:,.2f} ₽

📊 Количество транзакций: {len(transactions)}
📋 Активных бюджетов: {len(budget_statuses)}

📅 Отчет создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=12,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=1', facecolor='lightgray', alpha=0.8))
        
        plt.suptitle('Комплексный финансовый отчет', fontsize=18, fontweight='bold')
        plt.tight_layout()
        
        # Сохраняем график
        filename = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
