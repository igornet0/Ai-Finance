"""
Диалоги для добавления и редактирования данных
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, List

from ..core.models.transaction import Transaction, TransactionType
from ..core.models.category import Category, CategoryType
from ..core.models.budget import Budget, BudgetPeriod


class TransactionDialog:
    """
    Диалог для добавления/редактирования транзакции
    """
    
    def __init__(self, parent, main_window, transaction: Optional[Transaction] = None):
        """
        Инициализация диалога
        
        Args:
            parent: Родительский виджет
            main_window: Главное окно приложения
            transaction: Транзакция для редактирования (None для создания новой)
        """
        self.parent = parent
        self.main_window = main_window
        self.services = main_window.get_services()
        self.transaction = transaction
        self.result = None
        
        # Создаем диалог
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактировать транзакцию" if transaction else "Добавить транзакцию")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем диалог
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
        self._load_data()
        
        # Ожидаем закрытия диалога
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """Создание виджетов диалога"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Сумма
        ttk.Label(main_frame, text="Сумма:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var, width=20)
        self.amount_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Тип транзакции
        ttk.Label(main_frame, text="Тип:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                      values=["income", "expense"], state="readonly", width=17)
        self.type_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Категория
        ttk.Label(main_frame, text="Категория:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                          state="readonly", width=17)
        self.category_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Описание
        ttk.Label(main_frame, text="Описание:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(main_frame, textvariable=self.description_var, width=20)
        self.description_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Дата
        ttk.Label(main_frame, text="Дата:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(main_frame, textvariable=self.date_var, width=20)
        self.date_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Привязка событий
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)
        self.amount_entry.focus()
    
    def _load_data(self):
        """Загрузка данных в форму"""
        # Загружаем категории
        self._load_categories()
        
        if self.transaction:
            # Режим редактирования
            self.amount_var.set(str(self.transaction.amount))
            self.type_var.set(self.transaction.transaction_type.value)
            self.description_var.set(self.transaction.description)
            self.date_var.set(self.transaction.date.strftime('%Y-%m-%d'))
            
            # Устанавливаем категорию
            if self.transaction.category_id:
                category = self.services['category_service'].get_category(self.transaction.category_id)
                if category:
                    self.category_var.set(category.name)
        else:
            # Режим создания
            self.type_var.set("expense")
            self.date_var.set(date.today().strftime('%Y-%m-%d'))
        
        # Обновляем список категорий
        self._on_type_change()
    
    def _load_categories(self):
        """Загрузка списка категорий"""
        try:
            categories = self.services['category_service'].get_categories()
            category_names = [cat.name for cat in categories]
            self.category_combo['values'] = category_names
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить категории: {e}")
    
    def _on_type_change(self, event=None):
        """Обработка изменения типа транзакции"""
        # Фильтруем категории по типу
        try:
            transaction_type = TransactionType(self.type_var.get())
            if transaction_type == TransactionType.INCOME:
                categories = self.services['category_service'].get_categories(
                    category_type=CategoryType.INCOME
                )
            elif transaction_type == TransactionType.EXPENSE:
                categories = self.services['category_service'].get_categories(
                    category_type=CategoryType.EXPENSE
                )
            else:
                categories = self.services['category_service'].get_categories()
            
            category_names = [cat.name for cat in categories]
            self.category_combo['values'] = category_names
            
            # Сбрасываем выбранную категорию
            if not self.transaction:
                self.category_var.set("")
                
        except Exception as e:
            print(f"Ошибка при фильтрации категорий: {e}")
    
    def _save(self):
        """Сохранение транзакции"""
        try:
            # Валидация данных
            if not self.amount_var.get():
                messagebox.showerror("Ошибка", "Введите сумму")
                return
            
            try:
                amount = Decimal(self.amount_var.get())
            except InvalidOperation:
                messagebox.showerror("Ошибка", "Неверный формат суммы")
                return
            
            if not self.type_var.get():
                messagebox.showerror("Ошибка", "Выберите тип транзакции")
                return
            
            if not self.category_var.get():
                messagebox.showerror("Ошибка", "Выберите категорию")
                return
            
            # Парсим дату
            try:
                transaction_date = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты (YYYY-MM-DD)")
                return
            
            # Находим категорию
            categories = self.services['category_service'].search_categories(self.category_var.get())
            if not categories:
                messagebox.showerror("Ошибка", "Категория не найдена")
                return
            
            category = categories[0]
            
            # Создаем или обновляем транзакцию
            if self.transaction:
                # Режим редактирования
                self.transaction.amount = amount
                self.transaction.transaction_type = TransactionType(self.type_var.get())
                self.transaction.category_id = category.id
                self.transaction.description = self.description_var.get()
                self.transaction.date = transaction_date
                
                self.services['transaction_service'].update_transaction(self.transaction)
                messagebox.showinfo("Успех", "Транзакция обновлена")
            else:
                # Режим создания
                transaction = Transaction(
                    amount=amount,
                    transaction_type=TransactionType(self.type_var.get()),
                    category_id=category.id,
                    description=self.description_var.get(),
                    date=transaction_date
                )
                
                self.services['transaction_service'].create_transaction(transaction)
                messagebox.showinfo("Успех", "Транзакция добавлена")
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")
    
    def _cancel(self):
        """Отмена диалога"""
        self.result = False
        self.dialog.destroy()


class CategoryDialog:
    """
    Диалог для добавления/редактирования категории
    """
    
    def __init__(self, parent, main_window, category: Optional[Category] = None, parent_id: Optional[int] = None):
        """
        Инициализация диалога
        
        Args:
            parent: Родительский виджет
            main_window: Главное окно приложения
            category: Категория для редактирования (None для создания новой)
            parent_id: ID родительской категории (для создания подкатегории)
        """
        self.parent = parent
        self.main_window = main_window
        self.services = main_window.get_services()
        self.category = category
        self.parent_id = parent_id
        self.result = None
        
        # Создаем диалог
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактировать категорию" if category else "Добавить категорию")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем диалог
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
        self._load_data()
        
        # Ожидаем закрытия диалога
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """Создание виджетов диалога"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Название
        ttk.Label(main_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=20)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Описание
        ttk.Label(main_frame, text="Описание:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(main_frame, textvariable=self.description_var, width=20)
        self.description_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Тип категории
        ttk.Label(main_frame, text="Тип:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                      values=["income", "expense", "both"], state="readonly", width=17)
        self.type_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Родительская категория
        ttk.Label(main_frame, text="Родительская:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.parent_var = tk.StringVar()
        self.parent_combo = ttk.Combobox(main_frame, textvariable=self.parent_var, 
                                        state="readonly", width=17)
        self.parent_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Цвет
        ttk.Label(main_frame, text="Цвет:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.color_var = tk.StringVar()
        self.color_combo = ttk.Combobox(main_frame, textvariable=self.color_var, 
                                       values=["#3498db", "#2ecc71", "#e74c3c", "#f39c12", 
                                              "#9b59b6", "#1abc9c", "#34495e", "#95a5a6"], 
                                       state="readonly", width=17)
        self.color_combo.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Иконка
        ttk.Label(main_frame, text="Иконка:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.icon_var = tk.StringVar()
        self.icon_combo = ttk.Combobox(main_frame, textvariable=self.icon_var, 
                                      values=["📁", "💰", "💸", "🛒", "🚗", "🏠", "🎬", "🏥", 
                                             "👕", "📚", "💻", "📈", "🎁", "📦"], 
                                      state="readonly", width=17)
        self.icon_combo.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Активна
        self.active_var = tk.BooleanVar()
        self.active_check = ttk.Checkbutton(main_frame, text="Активна", variable=self.active_var)
        self.active_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Фокус на поле названия
        self.name_entry.focus()
    
    def _load_data(self):
        """Загрузка данных в форму"""
        # Загружаем родительские категории
        self._load_parent_categories()
        
        if self.category:
            # Режим редактирования
            self.name_var.set(self.category.name)
            self.description_var.set(self.category.description)
            self.type_var.set(self.category.category_type.value)
            self.color_var.set(self.category.color)
            self.icon_var.set(self.category.icon)
            self.active_var.set(self.category.is_active)
            
            # Устанавливаем родительскую категорию
            if self.category.parent_id:
                parent_category = self.services['category_service'].get_category(self.category.parent_id)
                if parent_category:
                    self.parent_var.set(parent_category.name)
        else:
            # Режим создания
            self.type_var.set("expense")
            self.color_var.set("#3498db")
            self.icon_var.set("📁")
            self.active_var.set(True)
            
            # Если указан parent_id, устанавливаем родительскую категорию
            if self.parent_id:
                parent_category = self.services['category_service'].get_category(self.parent_id)
                if parent_category:
                    self.parent_var.set(parent_category.name)
    
    def _load_parent_categories(self):
        """Загрузка списка родительских категорий"""
        try:
            categories = self.services['category_service'].get_root_categories()
            category_names = [cat.name for cat in categories]
            self.parent_combo['values'] = category_names
        except Exception as e:
            print(f"Ошибка при загрузке родительских категорий: {e}")
    
    def _save(self):
        """Сохранение категории"""
        try:
            # Валидация данных
            if not self.name_var.get():
                messagebox.showerror("Ошибка", "Введите название категории")
                return
            
            # Находим родительскую категорию
            parent_id = None
            if self.parent_var.get():
                parent_categories = self.services['category_service'].search_categories(self.parent_var.get())
                if parent_categories:
                    parent_id = parent_categories[0].id
            
            # Создаем или обновляем категорию
            if self.category:
                # Режим редактирования
                self.category.name = self.name_var.get()
                self.category.description = self.description_var.get()
                self.category.category_type = CategoryType(self.type_var.get())
                self.category.parent_id = parent_id
                self.category.color = self.color_var.get()
                self.category.icon = self.icon_var.get()
                self.category.is_active = self.active_var.get()
                
                self.services['category_service'].update_category(self.category)
                messagebox.showinfo("Успех", "Категория обновлена")
            else:
                # Режим создания
                category = Category(
                    name=self.name_var.get(),
                    description=self.description_var.get(),
                    category_type=CategoryType(self.type_var.get()),
                    parent_id=parent_id,
                    color=self.color_var.get(),
                    icon=self.icon_var.get(),
                    is_active=self.active_var.get()
                )
                
                self.services['category_service'].create_category(category)
                messagebox.showinfo("Успех", "Категория добавлена")
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")
    
    def _cancel(self):
        """Отмена диалога"""
        self.result = False
        self.dialog.destroy()


class BudgetDialog:
    """
    Диалог для добавления/редактирования бюджета
    """
    
    def __init__(self, parent, main_window, budget: Optional[Budget] = None):
        """
        Инициализация диалога
        
        Args:
            parent: Родительский виджет
            main_window: Главное окно приложения
            budget: Бюджет для редактирования (None для создания новой)
        """
        self.parent = parent
        self.main_window = main_window
        self.services = main_window.get_services()
        self.budget = budget
        self.result = None
        
        # Создаем диалог
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактировать бюджет" if budget else "Добавить бюджет")
        self.dialog.geometry("400x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем диалог
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
        self._load_data()
        
        # Ожидаем закрытия диалога
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """Создание виджетов диалога"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Название
        ttk.Label(main_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=20)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Категория
        ttk.Label(main_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                          state="readonly", width=17)
        self.category_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Сумма
        ttk.Label(main_frame, text="Сумма:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var, width=20)
        self.amount_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Период
        ttk.Label(main_frame, text="Период:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.period_var = tk.StringVar()
        self.period_combo = ttk.Combobox(main_frame, textvariable=self.period_var, 
                                        values=["daily", "weekly", "monthly", "yearly"], 
                                        state="readonly", width=17)
        self.period_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Начальная дата
        ttk.Label(main_frame, text="Начальная дата:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(main_frame, textvariable=self.start_date_var, width=20)
        self.start_date_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Конечная дата
        ttk.Label(main_frame, text="Конечная дата:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(main_frame, textvariable=self.end_date_var, width=20)
        self.end_date_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Порог предупреждения
        ttk.Label(main_frame, text="Порог предупреждения:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.threshold_var = tk.StringVar()
        self.threshold_entry = ttk.Entry(main_frame, textvariable=self.threshold_var, width=20)
        self.threshold_entry.grid(row=6, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Активен
        self.active_var = tk.BooleanVar()
        self.active_check = ttk.Checkbutton(main_frame, text="Активен", variable=self.active_var)
        self.active_check.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Фокус на поле названия
        self.name_entry.focus()
    
    def _load_data(self):
        """Загрузка данных в форму"""
        # Загружаем категории
        self._load_categories()
        
        if self.budget:
            # Режим редактирования
            self.name_var.set(self.budget.name)
            self.amount_var.set(str(self.budget.amount))
            self.period_var.set(self.budget.period.value)
            self.start_date_var.set(self.budget.start_date.strftime('%Y-%m-%d'))
            if self.budget.end_date:
                self.end_date_var.set(self.budget.end_date.strftime('%Y-%m-%d'))
            self.threshold_var.set(str(self.budget.alert_threshold))
            self.active_var.set(self.budget.is_active)
            
            # Устанавливаем категорию
            if self.budget.category_id:
                category = self.services['category_service'].get_category(self.budget.category_id)
                if category:
                    self.category_var.set(category.name)
        else:
            # Режим создания
            self.period_var.set("monthly")
            self.start_date_var.set(date.today().strftime('%Y-%m-%d'))
            self.threshold_var.set("0.80")
            self.active_var.set(True)
    
    def _load_categories(self):
        """Загрузка списка категорий"""
        try:
            categories = self.services['category_service'].get_categories()
            category_names = [cat.name for cat in categories]
            self.category_combo['values'] = category_names
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить категории: {e}")
    
    def _save(self):
        """Сохранение бюджета"""
        try:
            # Валидация данных
            if not self.name_var.get():
                messagebox.showerror("Ошибка", "Введите название бюджета")
                return
            
            if not self.amount_var.get():
                messagebox.showerror("Ошибка", "Введите сумму бюджета")
                return
            
            try:
                amount = Decimal(self.amount_var.get())
            except InvalidOperation:
                messagebox.showerror("Ошибка", "Неверный формат суммы")
                return
            
            if not self.start_date_var.get():
                messagebox.showerror("Ошибка", "Введите начальную дату")
                return
            
            try:
                start_date = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').date()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты (YYYY-MM-DD)")
                return
            
            # Парсим конечную дату
            end_date = None
            if self.end_date_var.get():
                try:
                    end_date = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').date()
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат конечной даты (YYYY-MM-DD)")
                    return
            
            # Парсим порог предупреждения
            try:
                threshold = Decimal(self.threshold_var.get())
            except InvalidOperation:
                messagebox.showerror("Ошибка", "Неверный формат порога предупреждения")
                return
            
            # Находим категорию
            category_id = None
            if self.category_var.get():
                categories = self.services['category_service'].search_categories(self.category_var.get())
                if categories:
                    category_id = categories[0].id
            
            # Создаем или обновляем бюджет
            if self.budget:
                # Режим редактирования
                self.budget.name = self.name_var.get()
                self.budget.category_id = category_id
                self.budget.amount = amount
                self.budget.period = BudgetPeriod(self.period_var.get())
                self.budget.start_date = start_date
                self.budget.end_date = end_date
                self.budget.alert_threshold = threshold
                self.budget.is_active = self.active_var.get()
                
                self.services['budget_service'].update_budget(self.budget)
                messagebox.showinfo("Успех", "Бюджет обновлен")
            else:
                # Режим создания
                budget = Budget(
                    name=self.name_var.get(),
                    category_id=category_id,
                    amount=amount,
                    period=BudgetPeriod(self.period_var.get()),
                    start_date=start_date,
                    end_date=end_date,
                    alert_threshold=threshold,
                    is_active=self.active_var.get()
                )
                
                self.services['budget_service'].create_budget(budget)
                messagebox.showinfo("Успех", "Бюджет добавлен")
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")
    
    def _cancel(self):
        """Отмена диалога"""
        self.result = False
        self.dialog.destroy()
