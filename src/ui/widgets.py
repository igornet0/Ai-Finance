"""
Виджеты для отображения данных
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from ..core.models.transaction import Transaction, TransactionType
from ..core.models.category import Category, CategoryType
from ..core.models.budget import Budget, BudgetPeriod


class TransactionTable:
    """
    Таблица для отображения транзакций
    """
    
    def __init__(self, parent, main_window):
        """
        Инициализация таблицы транзакций
        
        Args:
            parent: Родительский виджет
            main_window: Главное окно приложения
        """
        self.parent = parent
        self.main_window = main_window
        self.services = main_window.get_services()
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        """Создание виджетов таблицы"""
        # Панель управления
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки управления
        ttk.Button(control_frame, text="➕ Добавить", command=self._add_transaction).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="✏️ Редактировать", command=self._edit_transaction).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="🗑️ Удалить", command=self._delete_transaction).pack(side=tk.LEFT, padx=2)
        
        # Разделитель
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Фильтры
        ttk.Label(control_frame, text="Фильтр:").pack(side=tk.LEFT, padx=2)
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._on_filter_change)
        filter_entry = ttk.Entry(control_frame, textvariable=self.filter_var, width=20)
        filter_entry.pack(side=tk.LEFT, padx=2)
        
        # Кнопка обновления
        ttk.Button(control_frame, text="🔄 Обновить", command=self.refresh).pack(side=tk.RIGHT, padx=2)
        
        # Таблица транзакций
        columns = ("ID", "Дата", "Тип", "Сумма", "Категория", "Описание")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип", text="Тип")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Описание", text="Описание")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Дата", width=100, anchor=tk.CENTER)
        self.tree.column("Тип", width=80, anchor=tk.CENTER)
        self.tree.column("Сумма", width=120, anchor=tk.E)
        self.tree.column("Категория", width=120, anchor=tk.W)
        self.tree.column("Описание", width=200, anchor=tk.W)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        
        # Привязка событий
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)
    
    def refresh(self):
        """Обновление данных таблицы"""
        try:
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Получаем транзакции
            transactions = self.services['transaction_service'].get_transactions(limit=100)
            
            # Добавляем транзакции в таблицу
            for transaction in transactions:
                # Получаем категорию
                category_name = "Без категории"
                if transaction.category_id:
                    category = self.services['category_service'].get_category(transaction.category_id)
                    if category:
                        category_name = category.name
                
                # Форматируем данные
                type_icon = "💰" if transaction.is_income else "💸"
                amount_str = f"{transaction.amount:,.2f} ₽"
                if transaction.is_expense:
                    amount_str = f"-{amount_str}"
                
                # Добавляем в таблицу
                self.tree.insert("", tk.END, values=(
                    transaction.id,
                    transaction.date.strftime('%d.%m.%Y'),
                    type_icon,
                    amount_str,
                    category_name,
                    transaction.description
                ))
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить транзакции: {e}")
    
    def _on_filter_change(self, *args):
        """Обработка изменения фильтра"""
        filter_text = self.filter_var.get().lower()
        
        # Фильтруем элементы таблицы
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            # Проверяем описание и категорию
            if (filter_text in values[4].lower() or 
                filter_text in values[5].lower()):
                self.tree.reattach(item, '', 'end')
            else:
                self.tree.detach(item)
    
    def _on_double_click(self, event):
        """Обработка двойного клика"""
        self._edit_transaction()
    
    def _on_right_click(self, event):
        """Обработка правого клика"""
        # Создаем контекстное меню
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Редактировать", command=self._edit_transaction)
        context_menu.add_command(label="Удалить", command=self._delete_transaction)
        context_menu.add_separator()
        context_menu.add_command(label="Копировать", command=self._copy_transaction)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _add_transaction(self):
        """Добавление новой транзакции"""
        from .dialogs import TransactionDialog
        dialog = TransactionDialog(self.parent, self.main_window)
        if dialog.result:
            self.refresh()
    
    def _edit_transaction(self):
        """Редактирование транзакции"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите транзакцию для редактирования")
            return
        
        # Получаем ID транзакции
        item = self.tree.item(selected[0])
        transaction_id = int(item['values'][0])
        
        # Получаем транзакцию из базы
        transaction = self.services['transaction_service'].get_transaction(transaction_id)
        if not transaction:
            messagebox.showerror("Ошибка", "Транзакция не найдена")
            return
        
        # Открываем диалог редактирования
        from .dialogs import TransactionDialog
        dialog = TransactionDialog(self.parent, self.main_window, transaction)
        if dialog.result:
            self.refresh()
    
    def _delete_transaction(self):
        """Удаление транзакции"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите транзакцию для удаления")
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту транзакцию?"):
            return
        
        # Получаем ID транзакции
        item = self.tree.item(selected[0])
        transaction_id = int(item['values'][0])
        
        try:
            # Удаляем транзакцию
            success = self.services['transaction_service'].delete_transaction(transaction_id)
            if success:
                messagebox.showinfo("Успех", "Транзакция удалена")
                self.refresh()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить транзакцию")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")
    
    def _copy_transaction(self):
        """Копирование транзакции"""
        selected = self.tree.selection()
        if not selected:
            return
        
        # Получаем данные транзакции
        item = self.tree.item(selected[0])
        values = item['values']
        
        # Копируем в буфер обмена
        text = f"{values[1]} | {values[2]} | {values[3]} | {values[4]} | {values[5]}"
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)


class CategoryTree:
    """
    Дерево категорий
    """
    
    def __init__(self, parent, main_window):
        """
        Инициализация дерева категорий
        
        Args:
            parent: Родительский виджет
            main_window: Главное окно приложения
        """
        self.parent = parent
        self.main_window = main_window
        self.services = main_window.get_services()
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        """Создание виджетов дерева"""
        # Панель управления
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки управления
        ttk.Button(control_frame, text="➕ Добавить", command=self._add_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="✏️ Редактировать", command=self._edit_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="🗑️ Удалить", command=self._delete_category).pack(side=tk.LEFT, padx=2)
        
        # Разделитель
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Кнопка обновления
        ttk.Button(control_frame, text="🔄 Обновить", command=self.refresh).pack(side=tk.RIGHT, padx=2)
        
        # Дерево категорий
        self.tree = ttk.Treeview(self.parent, columns=("type", "icon", "active"), show="tree headings", height=15)
        
        # Настройка колонок
        self.tree.heading("#0", text="Название")
        self.tree.heading("type", text="Тип")
        self.tree.heading("icon", text="Иконка")
        self.tree.heading("active", text="Активна")
        
        self.tree.column("#0", width=200, anchor=tk.W)
        self.tree.column("type", width=80, anchor=tk.CENTER)
        self.tree.column("icon", width=60, anchor=tk.CENTER)
        self.tree.column("active", width=80, anchor=tk.CENTER)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Привязка событий
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)
    
    def refresh(self):
        """Обновление данных дерева"""
        try:
            # Очищаем дерево
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Получаем дерево категорий
            category_tree = self.services['category_service'].get_category_tree()
            
            # Добавляем категории в дерево
            self._add_categories_to_tree(category_tree, "")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить категории: {e}")
    
    def _add_categories_to_tree(self, categories: List[Dict], parent: str):
        """
        Рекурсивное добавление категорий в дерево
        
        Args:
            categories: Список категорий
            parent: ID родительского элемента
        """
        for category_data in categories:
            # Определяем тип
            type_icon = "💰" if category_data['category_type'] == 'income' else "💸"
            
            # Добавляем категорию
            item_id = self.tree.insert(parent, tk.END, 
                                     text=category_data['name'],
                                     values=(type_icon, category_data['icon'], 
                                            "✅" if category_data['is_active'] else "❌"))
            
            # Сохраняем ID категории в теге
            self.tree.set(item_id, "category_id", category_data['id'])
            
            # Добавляем дочерние категории
            if category_data['children']:
                self._add_categories_to_tree(category_data['children'], item_id)
    
    def _on_double_click(self, event):
        """Обработка двойного клика"""
        self._edit_category()
    
    def _on_right_click(self, event):
        """Обработка правого клика"""
        # Создаем контекстное меню
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Редактировать", command=self._edit_category)
        context_menu.add_command(label="Удалить", command=self._delete_category)
        context_menu.add_separator()
        context_menu.add_command(label="Добавить подкатегорию", command=self._add_subcategory)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _add_category(self):
        """Добавление новой категории"""
        from .dialogs import CategoryDialog
        dialog = CategoryDialog(self.parent, self.main_window)
        if dialog.result:
            self.refresh()
    
    def _add_subcategory(self):
        """Добавление подкатегории"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите родительскую категорию")
            return
        
        # Получаем ID родительской категории
        item = self.tree.item(selected[0])
        parent_id = int(self.tree.set(selected[0], "category_id"))
        
        from .dialogs import CategoryDialog
        dialog = CategoryDialog(self.parent, self.main_window, parent_id=parent_id)
        if dialog.result:
            self.refresh()
    
    def _edit_category(self):
        """Редактирование категории"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите категорию для редактирования")
            return
        
        # Получаем ID категории
        category_id = int(self.tree.set(selected[0], "category_id"))
        
        # Получаем категорию из базы
        category = self.services['category_service'].get_category(category_id)
        if not category:
            messagebox.showerror("Ошибка", "Категория не найдена")
            return
        
        # Открываем диалог редактирования
        from .dialogs import CategoryDialog
        dialog = CategoryDialog(self.parent, self.main_window, category)
        if dialog.result:
            self.refresh()
    
    def _delete_category(self):
        """Удаление категории"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите категорию для удаления")
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту категорию?"):
            return
        
        # Получаем ID категории
        category_id = int(self.tree.set(selected[0], "category_id"))
        
        try:
            # Удаляем категорию
            success = self.services['category_service'].delete_category(category_id)
            if success:
                messagebox.showinfo("Успех", "Категория удалена")
                self.refresh()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить категорию")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")


class BudgetList:
    """
    Список бюджетов
    """
    
    def __init__(self, parent, main_window):
        """
        Инициализация списка бюджетов
        
        Args:
            parent: Родительский виджет
            main_window: Главное окно приложения
        """
        self.parent = parent
        self.main_window = main_window
        self.services = main_window.get_services()
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        """Создание виджетов списка"""
        # Панель управления
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки управления
        ttk.Button(control_frame, text="➕ Добавить", command=self._add_budget).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="✏️ Редактировать", command=self._edit_budget).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="🗑️ Удалить", command=self._delete_budget).pack(side=tk.LEFT, padx=2)
        
        # Разделитель
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Кнопка обновления
        ttk.Button(control_frame, text="🔄 Обновить", command=self.refresh).pack(side=tk.RIGHT, padx=2)
        
        # Таблица бюджетов
        columns = ("Название", "Категория", "Лимит", "Потрачено", "Остаток", "Использование", "Статус")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        
        # Привязка событий
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)
    
    def refresh(self):
        """Обновление данных списка"""
        try:
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Получаем статус бюджетов
            budgets_status = self.services['budget_service'].get_all_budgets_status()
            
            # Добавляем бюджеты в таблицу
            for budget_status in budgets_status:
                # Определяем статус
                if budget_status['is_over_budget']:
                    status_icon = "🔴 Превышен"
                elif budget_status['is_near_limit']:
                    status_icon = "🟡 Близко к лимиту"
                else:
                    status_icon = "🟢 Норма"
                
                # Получаем название категории
                category_name = "Общий"
                if budget_status['budget_id']:
                    budget = self.services['budget_service'].get_budget(budget_status['budget_id'])
                    if budget and budget.category_id:
                        category = self.services['category_service'].get_category(budget.category_id)
                        if category:
                            category_name = category.name
                
                # Добавляем в таблицу
                self.tree.insert("", tk.END, values=(
                    budget_status['budget_name'],
                    category_name,
                    f"{budget_status['budget_amount']:,.2f} ₽",
                    f"{budget_status['spent_amount']:,.2f} ₽",
                    f"{budget_status['remaining_amount']:,.2f} ₽",
                    f"{budget_status['usage_percentage']:.1f}%",
                    status_icon
                ))
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бюджеты: {e}")
    
    def _on_double_click(self, event):
        """Обработка двойного клика"""
        self._edit_budget()
    
    def _on_right_click(self, event):
        """Обработка правого клика"""
        # Создаем контекстное меню
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Редактировать", command=self._edit_budget)
        context_menu.add_command(label="Удалить", command=self._delete_budget)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _add_budget(self):
        """Добавление нового бюджета"""
        from .dialogs import BudgetDialog
        dialog = BudgetDialog(self.parent, self.main_window)
        if dialog.result:
            self.refresh()
    
    def _edit_budget(self):
        """Редактирование бюджета"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бюджет для редактирования")
            return
        
        # Получаем данные бюджета
        item = self.tree.item(selected[0])
        budget_name = item['values'][0]
        
        # Находим бюджет по названию
        budgets = self.services['budget_service'].get_budgets()
        budget = next((b for b in budgets if b.name == budget_name), None)
        
        if not budget:
            messagebox.showerror("Ошибка", "Бюджет не найден")
            return
        
        # Открываем диалог редактирования
        from .dialogs import BudgetDialog
        dialog = BudgetDialog(self.parent, self.main_window, budget)
        if dialog.result:
            self.refresh()
    
    def _delete_budget(self):
        """Удаление бюджета"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бюджет для удаления")
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот бюджет?"):
            return
        
        # Получаем данные бюджета
        item = self.tree.item(selected[0])
        budget_name = item['values'][0]
        
        # Находим бюджет по названию
        budgets = self.services['budget_service'].get_budgets()
        budget = next((b for b in budgets if b.name == budget_name), None)
        
        if not budget:
            messagebox.showerror("Ошибка", "Бюджет не найден")
            return
        
        try:
            # Удаляем бюджет
            success = self.services['budget_service'].delete_budget(budget.id)
            if success:
                messagebox.showinfo("Успех", "Бюджет удален")
                self.refresh()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить бюджет")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")
