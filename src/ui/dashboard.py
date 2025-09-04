"""
Дашборд с основными показателями
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any

from ..core.calculators import BalanceCalculator, StatisticsCalculator


class DashboardWidget:
    """
    Виджет дашборда с основными финансовыми показателями
    """
    
    def __init__(self, parent, main_window):
        """
        Инициализация дашборда
        
        Args:
            parent: Родительский виджет
            main_window: Главное окно приложения
        """
        self.parent = parent
        self.main_window = main_window
        self.services = main_window.get_services()
        
        # Калькуляторы
        self.balance_calculator = BalanceCalculator()
        self.statistics_calculator = StatisticsCalculator()
        
        # Создание интерфейса
        self._create_widgets()
    
    def _create_widgets(self):
        """Создание виджетов дашборда"""
        # Основной фрейм с прокруткой
        canvas = tk.Canvas(self.parent)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Заголовок
        title_label = ttk.Label(scrollable_frame, text="📊 Финансовый дашборд", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Фрейм для карточек показателей
        self.cards_frame = ttk.Frame(scrollable_frame)
        self.cards_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Создаем карточки показателей
        self._create_balance_cards()
        
        # Фрейм для графиков и отчетов
        self.charts_frame = ttk.Frame(scrollable_frame)
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаем вкладки для разных видов отчетов
        self._create_report_tabs()
    
    def _create_balance_cards(self):
        """Создание карточек с основными показателями"""
        # Карточка общего баланса
        self.balance_card = self._create_card(
            self.cards_frame, "💳 Общий баланс", "0.00 ₽", "#3498db"
        )
        self.balance_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Карточка доходов за месяц
        self.income_card = self._create_card(
            self.cards_frame, "💰 Доходы (месяц)", "0.00 ₽", "#2ecc71"
        )
        self.income_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Карточка расходов за месяц
        self.expense_card = self._create_card(
            self.cards_frame, "💸 Расходы (месяц)", "0.00 ₽", "#e74c3c"
        )
        self.expense_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Карточка чистого дохода
        self.net_income_card = self._create_card(
            self.cards_frame, "📈 Чистый доход", "0.00 ₽", "#f39c12"
        )
        self.net_income_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    def _create_card(self, parent, title: str, value: str, color: str) -> ttk.Frame:
        """
        Создание карточки показателя
        
        Args:
            parent: Родительский виджет
            title: Заголовок карточки
            value: Значение
            color: Цвет карточки
        
        Returns:
            Фрейм карточки
        """
        card = ttk.Frame(parent, relief="solid", borderwidth=1)
        
        # Заголовок
        title_label = ttk.Label(card, text=title, font=("Arial", 10, "bold"))
        title_label.pack(pady=(10, 5))
        
        # Значение
        value_label = ttk.Label(card, text=value, font=("Arial", 14, "bold"))
        value_label.pack(pady=(0, 10))
        
        # Сохраняем ссылку на label для обновления
        card.value_label = value_label
        
        return card
    
    def _create_report_tabs(self):
        """Создание вкладок для отчетов"""
        # Notebook для вкладок
        self.report_notebook = ttk.Notebook(self.charts_frame)
        self.report_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка "Обзор"
        self.overview_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(self.overview_frame, text="📊 Обзор")
        self._create_overview_tab()
        
        # Вкладка "Анализ по категориям"
        self.categories_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(self.categories_frame, text="📁 По категориям")
        self._create_categories_tab()
        
        # Вкладка "Тренды"
        self.trends_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(self.trends_frame, text="📈 Тренды")
        self._create_trends_tab()
    
    def _create_overview_tab(self):
        """Создание вкладки обзора"""
        # Таблица с основными показателями
        columns = ("Показатель", "Текущий месяц", "Предыдущий месяц", "Изменение")
        self.overview_tree = ttk.Treeview(self.overview_frame, columns=columns, show="headings", height=8)
        
        # Настройка колонок
        for col in columns:
            self.overview_tree.heading(col, text=col)
            self.overview_tree.column(col, width=150, anchor=tk.CENTER)
        
        # Скроллбар
        overview_scrollbar = ttk.Scrollbar(self.overview_frame, orient=tk.VERTICAL, command=self.overview_tree.yview)
        self.overview_tree.configure(yscrollcommand=overview_scrollbar.set)
        
        # Размещение
        self.overview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        overview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _create_categories_tab(self):
        """Создание вкладки анализа по категориям"""
        # Таблица с категориями
        columns = ("Категория", "Тип", "Сумма", "Транзакций", "Средняя")
        self.categories_tree = ttk.Treeview(self.categories_frame, columns=columns, show="headings", height=10)
        
        # Настройка колонок
        for col in columns:
            self.categories_tree.heading(col, text=col)
            self.categories_tree.column(col, width=120, anchor=tk.CENTER)
        
        # Скроллбар
        categories_scrollbar = ttk.Scrollbar(self.categories_frame, orient=tk.VERTICAL, command=self.categories_tree.yview)
        self.categories_tree.configure(yscrollcommand=categories_scrollbar.set)
        
        # Размещение
        self.categories_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        categories_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _create_trends_tab(self):
        """Создание вкладки трендов"""
        # Заголовок
        trends_label = ttk.Label(self.trends_frame, text="📈 Анализ трендов за последние 12 месяцев", 
                                font=("Arial", 12, "bold"))
        trends_label.pack(pady=10)
        
        # Таблица с трендами
        columns = ("Месяц", "Доходы", "Расходы", "Чистый доход", "Тренд")
        self.trends_tree = ttk.Treeview(self.trends_frame, columns=columns, show="headings", height=12)
        
        # Настройка колонок
        for col in columns:
            self.trends_tree.heading(col, text=col)
            self.trends_tree.column(col, width=120, anchor=tk.CENTER)
        
        # Скроллбар
        trends_scrollbar = ttk.Scrollbar(self.trends_frame, orient=tk.VERTICAL, command=self.trends_tree.yview)
        self.trends_tree.configure(yscrollcommand=trends_scrollbar.set)
        
        # Размещение
        self.trends_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        trends_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def refresh(self):
        """Обновление данных дашборда"""
        try:
            # Получаем все транзакции
            transactions = self.services['transaction_service'].get_transactions()
            self.balance_calculator.add_transactions(transactions)
            self.statistics_calculator.add_transactions(transactions)
            
            # Обновляем карточки
            self._update_balance_cards()
            
            # Обновляем отчеты
            self._update_overview_tab()
            self._update_categories_tab()
            self._update_trends_tab()
            
        except Exception as e:
            print(f"Ошибка при обновлении дашборда: {e}")
    
    def _update_balance_cards(self):
        """Обновление карточек с балансом"""
        try:
            # Общий баланс
            total_balance = self.balance_calculator.calculate_balance()
            self.balance_card.value_label.config(text=f"{total_balance:,.2f} ₽")
            
            # Показатели за текущий месяц
            today = date.today()
            month_start = today.replace(day=1)
            
            month_income = self.balance_calculator.calculate_income(month_start, today)
            month_expenses = self.balance_calculator.calculate_expenses(month_start, today)
            month_net = self.balance_calculator.calculate_net_income(month_start, today)
            
            self.income_card.value_label.config(text=f"{month_income:,.2f} ₽")
            self.expense_card.value_label.config(text=f"{month_expenses:,.2f} ₽")
            self.net_income_card.value_label.config(text=f"{month_net:,.2f} ₽")
            
        except Exception as e:
            print(f"Ошибка при обновлении карточек: {e}")
    
    def _update_overview_tab(self):
        """Обновление вкладки обзора"""
        try:
            # Очищаем таблицу
            for item in self.overview_tree.get_children():
                self.overview_tree.delete(item)
            
            today = date.today()
            current_month_start = today.replace(day=1)
            
            # Предыдущий месяц
            if today.month == 1:
                prev_month_start = date(today.year - 1, 12, 1)
                prev_month_end = date(today.year - 1, 12, 31)
            else:
                prev_month_start = date(today.year, today.month - 1, 1)
                prev_month_end = date(today.year, today.month, 1) - timedelta(days=1)
            
            # Текущий месяц
            current_income = self.balance_calculator.calculate_income(current_month_start, today)
            current_expenses = self.balance_calculator.calculate_expenses(current_month_start, today)
            current_net = current_income - current_expenses
            
            # Предыдущий месяц
            prev_income = self.balance_calculator.calculate_income(prev_month_start, prev_month_end)
            prev_expenses = self.balance_calculator.calculate_expenses(prev_month_start, prev_month_end)
            prev_net = prev_income - prev_expenses
            
            # Добавляем данные в таблицу
            data = [
                ("Доходы", f"{current_income:,.2f} ₽", f"{prev_income:,.2f} ₽", 
                 self._format_change(current_income, prev_income)),
                ("Расходы", f"{current_expenses:,.2f} ₽", f"{prev_expenses:,.2f} ₽", 
                 self._format_change(current_expenses, prev_expenses)),
                ("Чистый доход", f"{current_net:,.2f} ₽", f"{prev_net:,.2f} ₽", 
                 self._format_change(current_net, prev_net))
            ]
            
            for row in data:
                self.overview_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            print(f"Ошибка при обновлении обзора: {e}")
    
    def _update_categories_tab(self):
        """Обновление вкладки категорий"""
        try:
            # Очищаем таблицу
            for item in self.categories_tree.get_children():
                self.categories_tree.delete(item)
            
            # Получаем анализ по категориям
            today = date.today()
            month_start = today.replace(day=1)
            category_analysis = self.statistics_calculator.get_category_analysis(month_start, today)
            
            # Добавляем данные в таблицу
            for category_data in category_analysis['categories']:
                category_id = category_data['category_id']
                category = self.services['category_service'].get_category(category_id)
                
                category_name = category.name if category else f"ID: {category_id}"
                category_type = "💰" if category_data['income'] > 0 else "💸"
                total_amount = category_data['income'] + category_data['expense']
                transaction_count = category_data['transaction_count']
                average = total_amount / transaction_count if transaction_count > 0 else 0
                
                self.categories_tree.insert("", tk.END, values=(
                    category_name,
                    category_type,
                    f"{total_amount:,.2f} ₽",
                    transaction_count,
                    f"{average:,.2f} ₽"
                ))
                
        except Exception as e:
            print(f"Ошибка при обновлении категорий: {e}")
    
    def _update_trends_tab(self):
        """Обновление вкладки трендов"""
        try:
            # Очищаем таблицу
            for item in self.trends_tree.get_children():
                self.trends_tree.delete(item)
            
            # Получаем анализ трендов
            trends_analysis = self.statistics_calculator.get_trend_analysis(12)
            
            # Добавляем данные в таблицу
            for month_data in trends_analysis['monthly_data']:
                month_name = f"{month_data['year']}-{month_data['month']:02d}"
                income = month_data['income']
                expenses = month_data['expenses']
                net_income = month_data['net_income']
                
                # Определяем тренд
                trend_icon = "📈" if net_income > 0 else "📉" if net_income < 0 else "➡️"
                
                self.trends_tree.insert("", tk.END, values=(
                    month_name,
                    f"{income:,.2f} ₽",
                    f"{expenses:,.2f} ₽",
                    f"{net_income:,.2f} ₽",
                    trend_icon
                ))
                
        except Exception as e:
            print(f"Ошибка при обновлении трендов: {e}")
    
    def _format_change(self, current: Decimal, previous: Decimal) -> str:
        """
        Форматирование изменения показателя
        
        Args:
            current: Текущее значение
            previous: Предыдущее значение
        
        Returns:
            Отформатированная строка изменения
        """
        if previous == 0:
            return "N/A"
        
        change = ((current - previous) / previous) * 100
        if change > 0:
            return f"+{change:.1f}% 📈"
        elif change < 0:
            return f"{change:.1f}% 📉"
        else:
            return "0% ➡️"
    
    def show_report(self):
        """Показать отчет (переключиться на вкладку обзора)"""
        self.report_notebook.select(0)
    
    def show_analysis(self):
        """Показать анализ (переключиться на вкладку категорий)"""
        self.report_notebook.select(1)
