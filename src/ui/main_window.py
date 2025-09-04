"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import threading

from ..data.database.initializer import DatabaseInitializer
from ..services import TransactionService, CategoryService, BudgetService, UserService
from .dashboard import DashboardWidget
from .widgets import TransactionTable, CategoryTree, BudgetList
from .dialogs import TransactionDialog, CategoryDialog, BudgetDialog


class MainWindow:
    """
    Главное окно приложения AI Finance
    """
    
    def __init__(self):
        """Инициализация главного окна"""
        self.root = tk.Tk()
        self.root.title("🏦 AI Finance - Личный финансовый калькулятор")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Инициализация сервисов
        self._init_services()
        
        # Создание интерфейса
        self._create_menu()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()
        
        # Загрузка данных
        self._load_data()
    
    def _init_services(self):
        """Инициализация сервисов базы данных"""
        try:
            self.db_initializer = DatabaseInitializer()
            self.db_initializer.initialize_database()
            
            self.transaction_service = self.db_initializer.transaction_service
            self.category_service = self.db_initializer.category_service
            self.budget_service = self.db_initializer.budget_service
            self.user_service = self.db_initializer.user_service
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось инициализировать базу данных: {e}")
            self.root.quit()
    
    def _create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новая транзакция", command=self._add_transaction)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт...", command=self._export_data)
        file_menu.add_command(label="Импорт...", command=self._import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Категории", command=self._manage_categories)
        edit_menu.add_command(label="Бюджеты", command=self._manage_budgets)
        
        # Меню "Отчеты"
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчеты", menu=reports_menu)
        reports_menu.add_command(label="Финансовый отчет", command=self._show_report)
        reports_menu.add_command(label="Анализ трат", command=self._show_analysis)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
    
    def _create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Кнопки быстрого доступа
        ttk.Button(toolbar, text="➕ Транзакция", command=self._add_transaction).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📁 Категории", command=self._manage_categories).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📋 Бюджеты", command=self._manage_budgets).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📊 Отчет", command=self._show_report).pack(side=tk.LEFT, padx=2)
        
        # Разделитель
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Кнопка обновления
        ttk.Button(toolbar, text="🔄 Обновить", command=self._refresh_data).pack(side=tk.LEFT, padx=2)
    
    def _create_main_content(self):
        """Создание основного контента"""
        # Создаем notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка "Дашборд"
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="📊 Дашборд")
        self.dashboard_widget = DashboardWidget(self.dashboard_frame, self)
        
        # Вкладка "Транзакции"
        self.transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_frame, text="💳 Транзакции")
        self.transaction_table = TransactionTable(self.transactions_frame, self)
        
        # Вкладка "Категории"
        self.categories_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.categories_frame, text="📁 Категории")
        self.category_tree = CategoryTree(self.categories_frame, self)
        
        # Вкладка "Бюджеты"
        self.budgets_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.budgets_frame, text="📋 Бюджеты")
        self.budget_list = BudgetList(self.budgets_frame, self)
    
    def _create_status_bar(self):
        """Создание строки состояния"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Готов")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Индикатор подключения к БД
        self.db_status_label = ttk.Label(self.status_bar, text="🟢 БД подключена")
        self.db_status_label.pack(side=tk.RIGHT, padx=5)
    
    def _load_data(self):
        """Загрузка данных в фоновом режиме"""
        def load():
            try:
                self.status_label.config(text="Загрузка данных...")
                # Обновляем все виджеты
                self.dashboard_widget.refresh()
                self.transaction_table.refresh()
                self.category_tree.refresh()
                self.budget_list.refresh()
                self.status_label.config(text="Готов")
            except Exception as e:
                self.status_label.config(text=f"Ошибка: {e}")
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        
        # Запускаем в отдельном потоке
        threading.Thread(target=load, daemon=True).start()
    
    def _add_transaction(self):
        """Добавление новой транзакции"""
        dialog = TransactionDialog(self.root, self)
        if dialog.result:
            self._refresh_data()
    
    def _manage_categories(self):
        """Управление категориями"""
        dialog = CategoryDialog(self.root, self)
        if dialog.result:
            self._refresh_data()
    
    def _manage_budgets(self):
        """Управление бюджетами"""
        dialog = BudgetDialog(self.root, self)
        if dialog.result:
            self._refresh_data()
    
    def _show_report(self):
        """Показать финансовый отчет"""
        # Переключаемся на вкладку дашборда
        self.notebook.select(0)
        self.dashboard_widget.show_report()
    
    def _show_analysis(self):
        """Показать анализ трат"""
        # Переключаемся на вкладку дашборда
        self.notebook.select(0)
        self.dashboard_widget.show_analysis()
    
    def _export_data(self):
        """Экспорт данных"""
        messagebox.showinfo("Экспорт", "Функция экспорта будет реализована в следующих версиях")
    
    def _import_data(self):
        """Импорт данных"""
        messagebox.showinfo("Импорт", "Функция импорта будет реализована в следующих версиях")
    
    def _show_about(self):
        """Показать информацию о программе"""
        about_text = """
🏦 AI Finance - Личный финансовый калькулятор
Версия 0.1.0

Управляйте своими финансами с помощью этого мощного инструмента.

Функции:
• Учет доходов и расходов
• Категоризация транзакций
• Бюджетирование
• Финансовые отчеты
• Анализ трат

Разработано с ❤️ на Python
        """
        messagebox.showinfo("О программе", about_text)
    
    def _refresh_data(self):
        """Обновление всех данных"""
        self._load_data()
    
    def run(self):
        """Запуск главного цикла приложения"""
        self.root.mainloop()
    
    def get_services(self):
        """Получить сервисы"""
        return {
            'transaction_service': self.transaction_service,
            'category_service': self.category_service,
            'budget_service': self.budget_service,
            'user_service': self.user_service
        }
