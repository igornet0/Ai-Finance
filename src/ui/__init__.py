"""
Модуль пользовательского интерфейса
"""

from .main_window import MainWindow
from .dialogs import TransactionDialog, CategoryDialog, BudgetDialog
from .widgets import TransactionTable, CategoryTree, BudgetList
from .dashboard import DashboardWidget

__all__ = [
    'MainWindow',
    'TransactionDialog',
    'CategoryDialog', 
    'BudgetDialog',
    'TransactionTable',
    'CategoryTree',
    'BudgetList',
    'DashboardWidget'
]
