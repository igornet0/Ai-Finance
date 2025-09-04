"""
Модуль импорта данных из различных форматов
"""

import pandas as pd
import csv
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import os
from pathlib import Path

from ...core.models.transaction import Transaction, TransactionType
from ...core.models.category import Category, CategoryType
from ...services import TransactionService, CategoryService


class DataImporter:
    """
    Класс для импорта данных из различных форматов
    """
    
    def __init__(self):
        """
        Инициализация импортера
        """
        pass
    
    def import_from_csv(self, file_path: str, 
                       transaction_service: TransactionService,
                       category_service: CategoryService,
                       date_format: str = '%d.%m.%Y',
                       skip_duplicates: bool = True) -> Dict[str, Any]:
        """
        Импорт транзакций из CSV файла
        
        Args:
            file_path: Путь к CSV файлу
            transaction_service: Сервис транзакций
            category_service: Сервис категорий
            date_format: Формат даты в файле
            skip_duplicates: Пропускать дубликаты
        
        Returns:
            Словарь с результатами импорта
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        results = {
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }
        
        try:
            # Читаем CSV файл
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # Проверяем наличие обязательных колонок
            required_columns = ['Дата', 'Тип', 'Сумма']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Отсутствуют обязательные колонки: {missing_columns}")
            
            # Получаем все существующие транзакции для проверки дубликатов
            existing_transactions = []
            if skip_duplicates:
                existing_transactions = transaction_service.get_transactions()
            
            # Получаем все категории
            categories = category_service.get_categories()
            category_dict = {cat.name.lower(): cat.id for cat in categories}
            
            # Обрабатываем каждую строку
            for index, row in df.iterrows():
                try:
                    # Парсим дату
                    if 'Время' in df.columns and pd.notna(row['Время']):
                        datetime_str = f"{row['Дата']} {row['Время']}"
                        transaction_date = datetime.strptime(datetime_str, f"{date_format} %H:%M:%S")
                    else:
                        transaction_date = datetime.strptime(str(row['Дата']), date_format)
                    
                    # Парсим тип транзакции
                    transaction_type_str = str(row['Тип']).lower()
                    if transaction_type_str in ['доход', 'income', 'приход']:
                        transaction_type = TransactionType.INCOME
                    elif transaction_type_str in ['расход', 'expense', 'уход']:
                        transaction_type = TransactionType.EXPENSE
                    else:
                        raise ValueError(f"Неизвестный тип транзакции: {row['Тип']}")
                    
                    # Парсим сумму
                    amount = Decimal(str(row['Сумма']))
                    if transaction_type == TransactionType.EXPENSE and amount > 0:
                        amount = -amount
                    elif transaction_type == TransactionType.INCOME and amount < 0:
                        amount = -amount
                    
                    # Парсим категорию
                    category_id = None
                    if 'Категория' in df.columns and pd.notna(row['Категория']):
                        category_name = str(row['Категория']).strip()
                        if category_name.lower() in category_dict:
                            category_id = category_dict[category_name.lower()]
                        else:
                            # Создаем новую категорию
                            new_category = Category(
                                name=category_name,
                                category_type=transaction_type,
                                description=f"Импортирована из {os.path.basename(file_path)}"
                            )
                            created_category = category_service.create_category(new_category)
                            category_id = created_category.id
                            category_dict[category_name.lower()] = category_id
                    
                    # Парсим описание
                    description = str(row['Описание']) if 'Описание' in df.columns and pd.notna(row['Описание']) else None
                    
                    # Парсим теги
                    tags = []
                    if 'Теги' in df.columns and pd.notna(row['Теги']):
                        tags_str = str(row['Теги']).strip()
                        if tags_str:
                            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                    
                    # Проверяем на дубликаты
                    if skip_duplicates:
                        is_duplicate = False
                        for existing in existing_transactions:
                            if (existing.date.date() == transaction_date.date() and
                                existing.amount == amount and
                                existing.transaction_type == transaction_type and
                                existing.description == description):
                                is_duplicate = True
                                break
                        
                        if is_duplicate:
                            results['skipped'] += 1
                            continue
                    
                    # Создаем транзакцию
                    transaction = Transaction(
                        amount=amount,
                        transaction_type=transaction_type,
                        category_id=category_id,
                        description=description,
                        tags=tags,
                        date=transaction_date
                    )
                    
                    # Сохраняем транзакцию
                    transaction_service.create_transaction(transaction)
                    results['imported'] += 1
                    
                except Exception as e:
                    results['errors'] += 1
                    results['error_details'].append(f"Строка {index + 2}: {str(e)}")
                    continue
        
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}")
        
        return results
    
    def import_from_excel(self, file_path: str,
                         transaction_service: TransactionService,
                         category_service: CategoryService,
                         sheet_name: str = 'Транзакции',
                         skip_duplicates: bool = True) -> Dict[str, Any]:
        """
        Импорт транзакций из Excel файла
        
        Args:
            file_path: Путь к Excel файлу
            transaction_service: Сервис транзакций
            category_service: Сервис категорий
            sheet_name: Имя листа с транзакциями
            skip_duplicates: Пропускать дубликаты
        
        Returns:
            Словарь с результатами импорта
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        results = {
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }
        
        try:
            # Читаем Excel файл
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Проверяем наличие обязательных колонок
            required_columns = ['Дата', 'Тип', 'Сумма']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Отсутствуют обязательные колонки: {missing_columns}")
            
            # Получаем все существующие транзакции для проверки дубликатов
            existing_transactions = []
            if skip_duplicates:
                existing_transactions = transaction_service.get_transactions()
            
            # Получаем все категории
            categories = category_service.get_categories()
            category_dict = {cat.name.lower(): cat.id for cat in categories}
            
            # Обрабатываем каждую строку
            for index, row in df.iterrows():
                try:
                    # Парсим дату
                    if isinstance(row['Дата'], pd.Timestamp):
                        transaction_date = row['Дата'].to_pydatetime()
                    else:
                        transaction_date = pd.to_datetime(row['Дата']).to_pydatetime()
                    
                    # Парсим тип транзакции
                    transaction_type_str = str(row['Тип']).lower()
                    if transaction_type_str in ['доход', 'income', 'приход']:
                        transaction_type = TransactionType.INCOME
                    elif transaction_type_str in ['расход', 'expense', 'уход']:
                        transaction_type = TransactionType.EXPENSE
                    else:
                        raise ValueError(f"Неизвестный тип транзакции: {row['Тип']}")
                    
                    # Парсим сумму
                    amount = Decimal(str(row['Сумма']))
                    if transaction_type == TransactionType.EXPENSE and amount > 0:
                        amount = -amount
                    elif transaction_type == TransactionType.INCOME and amount < 0:
                        amount = -amount
                    
                    # Парсим категорию
                    category_id = None
                    if 'Категория' in df.columns and pd.notna(row['Категория']):
                        category_name = str(row['Категория']).strip()
                        if category_name.lower() in category_dict:
                            category_id = category_dict[category_name.lower()]
                        else:
                            # Создаем новую категорию
                            new_category = Category(
                                name=category_name,
                                category_type=transaction_type,
                                description=f"Импортирована из {os.path.basename(file_path)}"
                            )
                            created_category = category_service.create_category(new_category)
                            category_id = created_category.id
                            category_dict[category_name.lower()] = category_id
                    
                    # Парсим описание
                    description = str(row['Описание']) if 'Описание' in df.columns and pd.notna(row['Описание']) else None
                    
                    # Парсим теги
                    tags = []
                    if 'Теги' in df.columns and pd.notna(row['Теги']):
                        tags_str = str(row['Теги']).strip()
                        if tags_str:
                            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                    
                    # Проверяем на дубликаты
                    if skip_duplicates:
                        is_duplicate = False
                        for existing in existing_transactions:
                            if (existing.date.date() == transaction_date.date() and
                                existing.amount == amount and
                                existing.transaction_type == transaction_type and
                                existing.description == description):
                                is_duplicate = True
                                break
                        
                        if is_duplicate:
                            results['skipped'] += 1
                            continue
                    
                    # Создаем транзакцию
                    transaction = Transaction(
                        amount=amount,
                        transaction_type=transaction_type,
                        category_id=category_id,
                        description=description,
                        tags=tags,
                        date=transaction_date
                    )
                    
                    # Сохраняем транзакцию
                    transaction_service.create_transaction(transaction)
                    results['imported'] += 1
                    
                except Exception as e:
                    results['errors'] += 1
                    results['error_details'].append(f"Строка {index + 2}: {str(e)}")
                    continue
        
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}")
        
        return results
    
    def import_bank_statement(self, file_path: str,
                             transaction_service: TransactionService,
                             category_service: CategoryService,
                             bank_name: str = "Банк",
                             date_format: str = '%d.%m.%Y',
                             skip_duplicates: bool = True) -> Dict[str, Any]:
        """
        Импорт банковской выписки
        
        Args:
            file_path: Путь к файлу выписки
            transaction_service: Сервис транзакций
            category_service: Сервис категорий
            bank_name: Название банка
            date_format: Формат даты в файле
            skip_duplicates: Пропускать дубликаты
        
        Returns:
            Словарь с результатами импорта
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        results = {
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }
        
        try:
            # Определяем формат файла
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_extension}")
            
            # Маппинг колонок для банковских выписок
            column_mapping = {
                'date': ['дата', 'date', 'дата операции', 'дата_операции'],
                'amount': ['сумма', 'amount', 'сумма операции', 'сумма_операции'],
                'description': ['описание', 'description', 'назначение', 'комментарий', 'примечание'],
                'type': ['тип', 'type', 'тип операции', 'тип_операции']
            }
            
            # Находим соответствующие колонки
            mapped_columns = {}
            for key, possible_names in column_mapping.items():
                for col in df.columns:
                    if col.lower() in [name.lower() for name in possible_names]:
                        mapped_columns[key] = col
                        break
            
            # Проверяем наличие обязательных колонок
            if 'date' not in mapped_columns or 'amount' not in mapped_columns:
                raise ValueError("Не найдены обязательные колонки: дата и сумма")
            
            # Получаем все существующие транзакции для проверки дубликатов
            existing_transactions = []
            if skip_duplicates:
                existing_transactions = transaction_service.get_transactions()
            
            # Получаем все категории
            categories = category_service.get_categories()
            category_dict = {cat.name.lower(): cat.id for cat in categories}
            
            # Обрабатываем каждую строку
            for index, row in df.iterrows():
                try:
                    # Парсим дату
                    date_col = mapped_columns['date']
                    if isinstance(row[date_col], pd.Timestamp):
                        transaction_date = row[date_col].to_pydatetime()
                    else:
                        transaction_date = pd.to_datetime(row[date_col], format=date_format).to_pydatetime()
                    
                    # Парсим сумму
                    amount_col = mapped_columns['amount']
                    amount = Decimal(str(row[amount_col]))
                    
                    # Определяем тип транзакции по знаку суммы
                    if amount > 0:
                        transaction_type = TransactionType.INCOME
                    else:
                        transaction_type = TransactionType.EXPENSE
                        amount = -amount  # Делаем положительным для хранения
                    
                    # Парсим описание
                    description = None
                    if 'description' in mapped_columns:
                        description = str(row[mapped_columns['description']]) if pd.notna(row[mapped_columns['description']]) else None
                    
                    # Автоматически определяем категорию по описанию
                    category_id = None
                    if description:
                        category_id = self._auto_categorize(description, category_dict, transaction_type)
                    
                    # Проверяем на дубликаты
                    if skip_duplicates:
                        is_duplicate = False
                        for existing in existing_transactions:
                            if (existing.date.date() == transaction_date.date() and
                                existing.amount == amount and
                                existing.transaction_type == transaction_type and
                                existing.description == description):
                                is_duplicate = True
                                break
                        
                        if is_duplicate:
                            results['skipped'] += 1
                            continue
                    
                    # Создаем транзакцию
                    transaction = Transaction(
                        amount=amount,
                        transaction_type=transaction_type,
                        category_id=category_id,
                        description=description,
                        tags=[bank_name],
                        date=transaction_date
                    )
                    
                    # Сохраняем транзакцию
                    transaction_service.create_transaction(transaction)
                    results['imported'] += 1
                    
                except Exception as e:
                    results['errors'] += 1
                    results['error_details'].append(f"Строка {index + 2}: {str(e)}")
                    continue
        
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}")
        
        return results
    
    def _auto_categorize(self, description: str, category_dict: Dict[str, int], 
                        transaction_type: TransactionType) -> Optional[int]:
        """
        Автоматическое определение категории по описанию
        
        Args:
            description: Описание транзакции
            category_dict: Словарь категорий
            transaction_type: Тип транзакции
        
        Returns:
            ID категории или None
        """
        description_lower = description.lower()
        
        # Ключевые слова для автоматической категоризации
        keywords = {
            'продукты': ['продукты', 'еда', 'магазин', 'супермаркет', 'продуктовый'],
            'транспорт': ['бензин', 'топливо', 'автобус', 'метро', 'такси', 'транспорт'],
            'развлечения': ['кино', 'театр', 'ресторан', 'кафе', 'развлечения'],
            'здоровье': ['аптека', 'врач', 'больница', 'медицина', 'здоровье'],
            'образование': ['школа', 'университет', 'курсы', 'образование', 'учеба'],
            'коммунальные': ['электричество', 'газ', 'вода', 'отопление', 'коммунальные'],
            'связь': ['телефон', 'интернет', 'связь', 'мобильный'],
            'одежда': ['одежда', 'обувь', 'магазин одежды', 'мода'],
            'зарплата': ['зарплата', 'заработная плата', 'доход', 'зарплата'],
            'инвестиции': ['инвестиции', 'депозит', 'акции', 'облигации']
        }
        
        for category_name, words in keywords.items():
            if category_name.lower() in category_dict:
                for word in words:
                    if word in description_lower:
                        return category_dict[category_name.lower()]
        
        return None
    
    def validate_import_file(self, file_path: str, file_type: str = 'csv') -> Dict[str, Any]:
        """
        Валидация файла перед импортом
        
        Args:
            file_path: Путь к файлу
            file_type: Тип файла ('csv' или 'excel')
        
        Returns:
            Словарь с результатами валидации
        """
        if not os.path.exists(file_path):
            return {'valid': False, 'error': 'Файл не найден'}
        
        try:
            if file_type == 'csv':
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            elif file_type == 'excel':
                df = pd.read_excel(file_path)
            else:
                return {'valid': False, 'error': 'Неподдерживаемый тип файла'}
            
            # Проверяем наличие обязательных колонок
            required_columns = ['Дата', 'Тип', 'Сумма']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    'valid': False,
                    'error': f'Отсутствуют обязательные колонки: {missing_columns}',
                    'available_columns': list(df.columns)
                }
            
            # Проверяем количество строк
            row_count = len(df)
            if row_count == 0:
                return {'valid': False, 'error': 'Файл пустой'}
            
            return {
                'valid': True,
                'row_count': row_count,
                'columns': list(df.columns),
                'sample_data': df.head(3).to_dict('records')
            }
        
        except Exception as e:
            return {'valid': False, 'error': f'Ошибка при чтении файла: {str(e)}'}
