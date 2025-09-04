"""
Инициализатор базы данных
"""

from pathlib import Path
from typing import Optional
from .database_manager import DatabaseManager
from ...services import TransactionService, CategoryService, BudgetService, UserService


class DatabaseInitializer:
    """
    Класс для инициализации базы данных с начальными данными
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Инициализация
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_manager = DatabaseManager(db_path)
        self.transaction_service = TransactionService(self.db_manager)
        self.category_service = CategoryService(self.db_manager)
        self.budget_service = BudgetService(self.db_manager)
        self.user_service = UserService(self.db_manager)
    
    def initialize_database(self, create_default_data: bool = True) -> bool:
        """
        Инициализирует базу данных
        
        Args:
            create_default_data: Создавать ли данные по умолчанию
        
        Returns:
            True если инициализация прошла успешно
        """
        try:
            # База данных уже создана в DatabaseManager.__init__
            
            if create_default_data:
                self._create_default_data()
            
            return True
        
        except Exception as e:
            print(f"Ошибка при инициализации базы данных: {e}")
            return False
    
    def _create_default_data(self) -> None:
        """Создает данные по умолчанию"""
        
        # Создаем пользователя по умолчанию
        default_user = self.user_service.get_or_create_default_user()
        print(f"✅ Создан пользователь по умолчанию: {default_user.username}")
        
        # Создаем категории по умолчанию
        default_categories = self.category_service.create_default_categories()
        print(f"✅ Создано {len(default_categories)} категорий по умолчанию")
        
        # Создаем примеры бюджетов
        self._create_example_budgets(default_categories)
        
        print("✅ База данных инициализирована с данными по умолчанию")
    
    def _create_example_budgets(self, categories: list) -> None:
        """Создает примеры бюджетов"""
        from ...core.models.budget import Budget, BudgetPeriod
        from datetime import date
        
        # Проверяем, есть ли уже бюджеты
        existing_budgets = self.budget_service.get_budgets()
        if existing_budgets:
            return
        
        # Находим категории для создания бюджетов
        food_category = next((cat for cat in categories if cat.name == "Продукты"), None)
        transport_category = next((cat for cat in categories if cat.name == "Транспорт"), None)
        entertainment_category = next((cat for cat in categories if cat.name == "Развлечения"), None)
        
        current_date = date.today()
        
        example_budgets = []
        
        if food_category:
            budget = Budget(
                name="Бюджет на продукты",
                category_id=food_category.id,
                amount=15000.00,  # 15,000 рублей
                period=BudgetPeriod.MONTHLY,
                start_date=current_date.replace(day=1),
                alert_threshold=0.80
            )
            example_budgets.append(budget)
        
        if transport_category:
            budget = Budget(
                name="Бюджет на транспорт",
                category_id=transport_category.id,
                amount=5000.00,  # 5,000 рублей
                period=BudgetPeriod.MONTHLY,
                start_date=current_date.replace(day=1),
                alert_threshold=0.90
            )
            example_budgets.append(budget)
        
        if entertainment_category:
            budget = Budget(
                name="Бюджет на развлечения",
                category_id=entertainment_category.id,
                amount=8000.00,  # 8,000 рублей
                period=BudgetPeriod.MONTHLY,
                start_date=current_date.replace(day=1),
                alert_threshold=0.75
            )
            example_budgets.append(budget)
        
        # Создаем бюджеты
        for budget in example_budgets:
            try:
                self.budget_service.create_budget(budget)
                print(f"✅ Создан бюджет: {budget.name}")
            except Exception as e:
                print(f"⚠️  Ошибка при создании бюджета '{budget.name}': {e}")
    
    def reset_database(self) -> bool:
        """
        Сбрасывает базу данных (удаляет все данные)
        
        Returns:
            True если сброс прошел успешно
        """
        try:
            # Удаляем все таблицы
            with self.db_manager.get_connection() as conn:
                conn.execute("DROP TABLE IF EXISTS transactions")
                conn.execute("DROP TABLE IF EXISTS budgets")
                conn.execute("DROP TABLE IF EXISTS categories")
                conn.execute("DROP TABLE IF EXISTS accounts")
                conn.execute("DROP TABLE IF EXISTS users")
                conn.commit()
            
            # Пересоздаем таблицы
            self.db_manager._initialize_database()
            
            print("✅ База данных сброшена")
            return True
        
        except Exception as e:
            print(f"Ошибка при сбросе базы данных: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """
        Получает информацию о базе данных
        
        Returns:
            Словарь с информацией о базе данных
        """
        return {
            'database_path': self.db_manager.db_path,
            'database_size': self.db_manager.get_database_size(),
            'tables': {
                'users': self.db_manager.get_table_count('users'),
                'categories': self.db_manager.get_table_count('categories'),
                'transactions': self.db_manager.get_table_count('transactions'),
                'budgets': self.db_manager.get_table_count('budgets'),
                'accounts': self.db_manager.get_table_count('accounts')
            }
        }
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Создает резервную копию базы данных
        
        Args:
            backup_path: Путь для сохранения резервной копии
        
        Returns:
            True если резервная копия создана успешно
        """
        return self.db_manager.backup_database(backup_path)
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Восстанавливает базу данных из резервной копии
        
        Args:
            backup_path: Путь к резервной копии
        
        Returns:
            True если восстановление прошло успешно
        """
        return self.db_manager.restore_database(backup_path)
