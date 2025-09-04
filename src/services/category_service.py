"""
Сервис для работы с категориями
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from ..core.models.category import Category, CategoryType
from ..data.database.database_manager import DatabaseManager
from ..data.database.models import CategoryModel


class CategoryService:
    """
    Сервис для управления категориями
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация сервиса
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db = db_manager
        self.model = CategoryModel()
    
    def create_category(self, category: Category) -> Category:
        """
        Создает новую категорию
        
        Args:
            category: Категория для создания
        
        Returns:
            Созданная категория с ID
        """
        category.created_at = datetime.now()
        category.updated_at = datetime.now()
        
        data = self.model.to_db_dict(category)
        # Убираем ID из данных для вставки
        data.pop('id', None)
        
        query = self.model.get_insert_query()
        params = (
            data['name'],
            data['description'],
            data['category_type'],
            data['parent_id'],
            data['color'],
            data['icon'],
            data['is_active'],
            data['created_at'],
            data['updated_at']
        )
        
        category_id = self.db.execute_update(query, params)
        category.id = category_id
        
        return category
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """
        Получает категорию по ID
        
        Args:
            category_id: ID категории
        
        Returns:
            Категория или None если не найдена
        """
        query = f"{self.model.get_select_query()} WHERE id = ?"
        rows = self.db.execute_query(query, (category_id,))
        
        if rows:
            return self.model.from_db_row(dict(rows[0]))
        return None
    
    def update_category(self, category: Category) -> Category:
        """
        Обновляет категорию
        
        Args:
            category: Категория для обновления
        
        Returns:
            Обновленная категория
        """
        category.updated_at = datetime.now()
        
        data = self.model.to_db_dict(category)
        query = self.model.get_update_query()
        params = (
            data['name'],
            data['description'],
            data['category_type'],
            data['parent_id'],
            data['color'],
            data['icon'],
            data['is_active'],
            data['updated_at'],
            data['id']
        )
        
        self.db.execute_update(query, params)
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """
        Удаляет категорию
        
        Args:
            category_id: ID категории
        
        Returns:
            True если категория удалена успешно
        """
        # Проверяем, есть ли дочерние категории
        children = self.get_child_categories(category_id)
        if children:
            raise ValueError("Нельзя удалить категорию с дочерними категориями")
        
        # Проверяем, есть ли транзакции с этой категорией
        query = "SELECT COUNT(*) as count FROM transactions WHERE category_id = ?"
        rows = self.db.execute_query(query, (category_id,))
        transaction_count = rows[0]['count'] if rows else 0
        
        if transaction_count > 0:
            raise ValueError("Нельзя удалить категорию с существующими транзакциями")
        
        query = self.model.get_delete_query()
        rows_affected = self.db.execute_update(query, (category_id,))
        return rows_affected > 0
    
    def get_categories(self, 
                      category_type: Optional[CategoryType] = None,
                      parent_id: Optional[int] = None,
                      is_active: Optional[bool] = None) -> List[Category]:
        """
        Получает список категорий с фильтрацией
        
        Args:
            category_type: Тип категории
            parent_id: ID родительской категории
            is_active: Активность категории
        
        Returns:
            Список категорий
        """
        query = self.model.get_select_query()
        conditions = []
        params = []
        
        if category_type:
            conditions.append("category_type = ?")
            params.append(category_type.value)
        
        if parent_id is not None:
            conditions.append("parent_id = ?")
            params.append(parent_id)
        
        if is_active is not None:
            conditions.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY name ASC"
        
        rows = self.db.execute_query(query, tuple(params))
        return [self.model.from_db_row(dict(row)) for row in rows]
    
    def get_child_categories(self, parent_id: int) -> List[Category]:
        """
        Получает дочерние категории
        
        Args:
            parent_id: ID родительской категории
        
        Returns:
            Список дочерних категорий
        """
        return self.get_categories(parent_id=parent_id)
    
    def get_root_categories(self, category_type: Optional[CategoryType] = None) -> List[Category]:
        """
        Получает корневые категории (без родителя)
        
        Args:
            category_type: Тип категории
        
        Returns:
            Список корневых категорий
        """
        return self.get_categories(parent_id=None, category_type=category_type)
    
    def get_category_tree(self, category_type: Optional[CategoryType] = None) -> List[Dict[str, Any]]:
        """
        Получает дерево категорий
        
        Args:
            category_type: Тип категории
        
        Returns:
            Список категорий с дочерними элементами
        """
        # Получаем все категории
        all_categories = self.get_categories(category_type=category_type)
        
        # Создаем словарь для быстрого поиска
        categories_dict = {cat.id: cat for cat in all_categories}
        
        # Строим дерево
        tree = []
        for category in all_categories:
            if category.parent_id is None:
                tree.append(self._build_category_node(category, categories_dict))
        
        return tree
    
    def _build_category_node(self, category: Category, 
                           categories_dict: Dict[int, Category]) -> Dict[str, Any]:
        """
        Строит узел дерева категорий
        
        Args:
            category: Категория
            categories_dict: Словарь всех категорий
        
        Returns:
            Узел дерева с дочерними элементами
        """
        node = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'category_type': category.category_type.value,
            'parent_id': category.parent_id,
            'color': category.color,
            'icon': category.icon,
            'is_active': category.is_active,
            'children': []
        }
        
        # Находим дочерние категории
        for cat_id, cat in categories_dict.items():
            if cat.parent_id == category.id:
                child_node = self._build_category_node(cat, categories_dict)
                node['children'].append(child_node)
        
        return node
    
    def search_categories(self, search_term: str) -> List[Category]:
        """
        Поиск категорий по названию
        
        Args:
            search_term: Поисковый запрос
        
        Returns:
            Список найденных категорий
        """
        query = f"""
            {self.model.get_select_query()}
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name ASC
        """
        search_pattern = f"%{search_term}%"
        rows = self.db.execute_query(query, (search_pattern, search_pattern))
        
        return [self.model.from_db_row(dict(row)) for row in rows]
    
    def get_category_usage_stats(self, category_id: int) -> Dict[str, Any]:
        """
        Получает статистику использования категории
        
        Args:
            category_id: ID категории
        
        Returns:
            Словарь со статистикой
        """
        # Количество транзакций
        query = """
            SELECT 
                transaction_type,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM transactions
            WHERE category_id = ?
            GROUP BY transaction_type
        """
        rows = self.db.execute_query(query, (category_id,))
        
        stats = {
            'category_id': category_id,
            'transaction_count': 0,
            'total_income': 0.0,
            'total_expense': 0.0,
            'by_type': {}
        }
        
        for row in rows:
            transaction_type = row['transaction_type']
            count = row['count']
            total_amount = row['total_amount'] or 0
            
            stats['by_type'][transaction_type] = {
                'count': count,
                'total_amount': float(total_amount)
            }
            
            stats['transaction_count'] += count
            
            if transaction_type == 'income':
                stats['total_income'] = float(total_amount)
            elif transaction_type == 'expense':
                stats['total_expense'] = float(total_amount)
        
        return stats
    
    def create_default_categories(self) -> List[Category]:
        """
        Создает категории по умолчанию
        
        Returns:
            Список созданных категорий
        """
        default_categories = [
            # Доходы
            Category(name="Зарплата", category_type=CategoryType.INCOME, 
                   description="Основная заработная плата", color="#27ae60", icon="💰"),
            Category(name="Подработка", category_type=CategoryType.INCOME,
                   description="Дополнительные доходы", color="#2ecc71", icon="💼"),
            Category(name="Инвестиции", category_type=CategoryType.INCOME,
                   description="Доходы от инвестиций", color="#16a085", icon="📈"),
            Category(name="Подарки", category_type=CategoryType.INCOME,
                   description="Подарки и бонусы", color="#f39c12", icon="🎁"),
            
            # Расходы
            Category(name="Продукты", category_type=CategoryType.EXPENSE,
                   description="Продукты питания", color="#e74c3c", icon="🛒"),
            Category(name="Транспорт", category_type=CategoryType.EXPENSE,
                   description="Транспортные расходы", color="#3498db", icon="🚗"),
            Category(name="Жилье", category_type=CategoryType.EXPENSE,
                   description="Аренда, коммунальные услуги", color="#9b59b6", icon="🏠"),
            Category(name="Развлечения", category_type=CategoryType.EXPENSE,
                   description="Развлечения и досуг", color="#e67e22", icon="🎬"),
            Category(name="Здоровье", category_type=CategoryType.EXPENSE,
                   description="Медицинские расходы", color="#1abc9c", icon="🏥"),
            Category(name="Одежда", category_type=CategoryType.EXPENSE,
                   description="Одежда и обувь", color="#f1c40f", icon="👕"),
            Category(name="Образование", category_type=CategoryType.EXPENSE,
                   description="Образование и обучение", color="#34495e", icon="📚"),
            Category(name="Прочее", category_type=CategoryType.EXPENSE,
                   description="Прочие расходы", color="#95a5a6", icon="📦")
        ]
        
        created_categories = []
        for category in default_categories:
            try:
                created_category = self.create_category(category)
                created_categories.append(created_category)
            except Exception as e:
                # Если категория уже существует, пропускаем
                print(f"Категория '{category.name}' уже существует: {e}")
        
        return created_categories
    
    def get_category_count(self) -> int:
        """
        Получает общее количество категорий
        
        Returns:
            Количество категорий
        """
        return self.db.get_table_count('categories')
