"""
Модуль экспорта данных в различные форматы
"""

import pandas as pd
import xlsxwriter
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from decimal import Decimal
import os
from pathlib import Path

from ...core.models.transaction import Transaction, TransactionType
from ...core.models.category import Category
from ...core.models.budget import Budget
from ...core.calculators import StatisticsCalculator, BalanceCalculator


class DataExporter:
    """
    Класс для экспорта данных в различные форматы
    """
    
    def __init__(self, output_dir: str = "exports"):
        """
        Инициализация экспортера
        
        Args:
            output_dir: Директория для сохранения экспортированных файлов
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_csv(self, transactions: List[Transaction],
                     categories: List[Category] = None,
                     filename: Optional[str] = None) -> str:
        """
        Экспорт транзакций в CSV файл
        
        Args:
            transactions: Список транзакций
            categories: Список категорий (опционально)
            filename: Имя файла (опционально)
        
        Returns:
            Путь к созданному файлу
        """
        if not transactions:
            raise ValueError("Нет транзакций для экспорта")
        
        # Создаем словарь категорий для быстрого поиска
        category_dict = {}
        if categories:
            category_dict = {cat.id: cat for cat in categories}
        
        # Подготавливаем данные
        data = []
        for transaction in transactions:
            category_name = "Без категории"
            if transaction.category_id and transaction.category_id in category_dict:
                category_name = category_dict[transaction.category_id].name
            
            data.append({
                'ID': transaction.id,
                'Дата': transaction.date.strftime('%d.%m.%Y'),
                'Время': transaction.date.strftime('%H:%M:%S'),
                'Тип': transaction.transaction_type.value,
                'Сумма': float(transaction.amount),
                'Категория': category_name,
                'Описание': transaction.description or '',
                'Теги': ', '.join(transaction.tags) if transaction.tags else '',
                'Создано': transaction.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                'Обновлено': transaction.updated_at.strftime('%d.%m.%Y %H:%M:%S')
            })
        
        # Создаем DataFrame
        df = pd.DataFrame(data)
        
        # Сортируем по дате (новые сначала)
        df = df.sort_values('Дата', ascending=False)
        
        # Генерируем имя файла
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"transactions_export_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # Сохраняем в CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return str(filepath)
    
    def export_to_excel(self, transactions: List[Transaction],
                       categories: List[Category] = None,
                       budgets: List[Budget] = None,
                       filename: Optional[str] = None) -> str:
        """
        Экспорт данных в Excel файл с несколькими листами
        
        Args:
            transactions: Список транзакций
            categories: Список категорий (опционально)
            budgets: Список бюджетов (опционально)
            filename: Имя файла (опционально)
        
        Returns:
            Путь к созданному файлу
        """
        if not transactions:
            raise ValueError("Нет транзакций для экспорта")
        
        # Генерируем имя файла
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"finance_export_{timestamp}.xlsx"
        
        filepath = self.output_dir / filename
        
        # Создаем словарь категорий
        category_dict = {}
        if categories:
            category_dict = {cat.id: cat for cat in categories}
        
        # Создаем Excel файл
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Стили
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            money_format = workbook.add_format({'num_format': '#,##0.00'})
            date_format = workbook.add_format({'num_format': 'dd.mm.yyyy'})
            
            # Лист 1: Транзакции
            transaction_data = []
            for transaction in transactions:
                category_name = "Без категории"
                if transaction.category_id and transaction.category_id in category_dict:
                    category_name = category_dict[transaction.category_id].name
                
                transaction_data.append({
                    'ID': transaction.id,
                    'Дата': transaction.date.date(),
                    'Время': transaction.date.time(),
                    'Тип': transaction.transaction_type.value,
                    'Сумма': float(transaction.amount),
                    'Категория': category_name,
                    'Описание': transaction.description or '',
                    'Теги': ', '.join(transaction.tags) if transaction.tags else '',
                    'Создано': transaction.created_at.date(),
                    'Обновлено': transaction.updated_at.date()
                })
            
            df_transactions = pd.DataFrame(transaction_data)
            df_transactions = df_transactions.sort_values('Дата', ascending=False)
            
            df_transactions.to_excel(writer, sheet_name='Транзакции', index=False)
            
            # Форматируем лист транзакций
            worksheet = writer.sheets['Транзакции']
            worksheet.set_column('A:A', 8)  # ID
            worksheet.set_column('B:B', 12)  # Дата
            worksheet.set_column('C:C', 10)  # Время
            worksheet.set_column('D:D', 12)  # Тип
            worksheet.set_column('E:E', 15, money_format)  # Сумма
            worksheet.set_column('F:F', 20)  # Категория
            worksheet.set_column('G:G', 30)  # Описание
            worksheet.set_column('H:H', 20)  # Теги
            worksheet.set_column('I:I', 12, date_format)  # Создано
            worksheet.set_column('J:J', 12, date_format)  # Обновлено
            
            # Заголовки
            for col_num, value in enumerate(df_transactions.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Лист 2: Категории
            if categories:
                category_data = []
                for category in categories:
                    category_data.append({
                        'ID': category.id,
                        'Название': category.name,
                        'Тип': category.category_type.value,
                        'Описание': category.description or '',
                        'Родительская': category.parent_id or '',
                        'Цвет': category.color or '',
                        'Иконка': category.icon or '',
                        'Активна': category.is_active,
                        'Создана': category.created_at.date()
                    })
                
                df_categories = pd.DataFrame(category_data)
                df_categories.to_excel(writer, sheet_name='Категории', index=False)
                
                # Форматируем лист категорий
                worksheet = writer.sheets['Категории']
                worksheet.set_column('A:A', 8)  # ID
                worksheet.set_column('B:B', 20)  # Название
                worksheet.set_column('C:C', 12)  # Тип
                worksheet.set_column('D:D', 30)  # Описание
                worksheet.set_column('E:E', 15)  # Родительская
                worksheet.set_column('F:F', 10)  # Цвет
                worksheet.set_column('G:G', 10)  # Иконка
                worksheet.set_column('H:H', 10)  # Активна
                worksheet.set_column('I:I', 12, date_format)  # Создана
                
                # Заголовки
                for col_num, value in enumerate(df_categories.columns.values):
                    worksheet.write(0, col_num, value, header_format)
            
            # Лист 3: Бюджеты
            if budgets:
                budget_data = []
                for budget in budgets:
                    category_name = "Без категории"
                    if budget.category_id and budget.category_id in category_dict:
                        category_name = category_dict[budget.category_id].name
                    
                    budget_data.append({
                        'ID': budget.id,
                        'Название': budget.name,
                        'Категория': category_name,
                        'Сумма': float(budget.amount),
                        'Период': budget.period.value,
                        'Начало': budget.start_date,
                        'Конец': budget.end_date,
                        'Порог': float(budget.alert_threshold) if budget.alert_threshold else 0,
                        'Активен': budget.is_active,
                        'Создан': budget.created_at.date()
                    })
                
                df_budgets = pd.DataFrame(budget_data)
                df_budgets.to_excel(writer, sheet_name='Бюджеты', index=False)
                
                # Форматируем лист бюджетов
                worksheet = writer.sheets['Бюджеты']
                worksheet.set_column('A:A', 8)  # ID
                worksheet.set_column('B:B', 25)  # Название
                worksheet.set_column('C:C', 20)  # Категория
                worksheet.set_column('D:D', 15, money_format)  # Сумма
                worksheet.set_column('E:E', 12)  # Период
                worksheet.set_column('F:F', 12, date_format)  # Начало
                worksheet.set_column('G:G', 12, date_format)  # Конец
                worksheet.set_column('H:H', 12, money_format)  # Порог
                worksheet.set_column('I:I', 10)  # Активен
                worksheet.set_column('J:J', 12, date_format)  # Создан
                
                # Заголовки
                for col_num, value in enumerate(df_budgets.columns.values):
                    worksheet.write(0, col_num, value, header_format)
            
            # Лист 4: Сводка
            summary_data = self._generate_summary_data(transactions, categories, budgets)
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Сводка', index=False)
            
            # Форматируем лист сводки
            worksheet = writer.sheets['Сводка']
            worksheet.set_column('A:A', 30)  # Показатель
            worksheet.set_column('B:B', 20)  # Значение
            worksheet.set_column('C:C', 30)  # Описание
            
            # Заголовки
            for col_num, value in enumerate(df_summary.columns.values):
                worksheet.write(0, col_num, value, header_format)
        
        return str(filepath)
    
    def export_to_pdf(self, transactions: List[Transaction],
                     categories: List[Category] = None,
                     budgets: List[Budget] = None,
                     filename: Optional[str] = None) -> str:
        """
        Экспорт данных в PDF отчет
        
        Args:
            transactions: Список транзакций
            categories: Список категорий (опционально)
            budgets: Список бюджетов (опционально)
            filename: Имя файла (опционально)
        
        Returns:
            Путь к созданному файлу
        """
        if not transactions:
            raise ValueError("Нет транзакций для экспорта")
        
        # Генерируем имя файла
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"finance_report_{timestamp}.pdf"
        
        filepath = self.output_dir / filename
        
        # Создаем PDF документ
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        
        # Стили
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Центрирование
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12
        )
        
        # Заголовок
        title = Paragraph("Финансовый отчет", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Информация о отчете
        report_info = f"""
        <b>Дата создания:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>
        <b>Количество транзакций:</b> {len(transactions)}<br/>
        <b>Период:</b> {min(t.date.date() for t in transactions).strftime('%d.%m.%Y')} - {max(t.date.date() for t in transactions).strftime('%d.%m.%Y')}
        """
        story.append(Paragraph(report_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Сводная статистика
        story.append(Paragraph("Сводная статистика", heading_style))
        
        # Рассчитываем статистику
        statistics_calculator = StatisticsCalculator()
        statistics_calculator.add_transactions(transactions)
        
        # Получаем общую статистику
        total_income = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.INCOME)
        total_expenses = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.EXPENSE)
        net_income = total_income - total_expenses
        
        # Создаем таблицу статистики
        stats_data = [
            ['Показатель', 'Значение'],
            ['Общие доходы', f'{total_income:,.2f} ₽'],
            ['Общие расходы', f'{total_expenses:,.2f} ₽'],
            ['Чистый доход', f'{net_income:,.2f} ₽'],
            ['Количество транзакций', str(len(transactions))],
            ['Средняя транзакция', f'{sum(float(t.amount) for t in transactions) / len(transactions):,.2f} ₽']
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Топ-10 транзакций
        story.append(Paragraph("Последние 10 транзакций", heading_style))
        
        # Сортируем транзакции по дате
        sorted_transactions = sorted(transactions, key=lambda x: x.date, reverse=True)[:10]
        
        # Создаем словарь категорий
        category_dict = {}
        if categories:
            category_dict = {cat.id: cat for cat in categories}
        
        # Подготавливаем данные для таблицы
        table_data = [['Дата', 'Тип', 'Сумма', 'Категория', 'Описание']]
        
        for transaction in sorted_transactions:
            category_name = "Без категории"
            if transaction.category_id and transaction.category_id in category_dict:
                category_name = category_dict[transaction.category_id].name
            
            table_data.append([
                transaction.date.strftime('%d.%m.%Y'),
                transaction.transaction_type.value,
                f'{float(transaction.amount):,.2f} ₽',
                category_name,
                transaction.description or ''
            ])
        
        transactions_table = Table(table_data)
        transactions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(transactions_table)
        story.append(Spacer(1, 20))
        
        # Анализ по категориям
        if categories:
            story.append(Paragraph("Анализ по категориям", heading_style))
            
            # Группируем транзакции по категориям
            category_stats = {}
            for transaction in transactions:
                category_name = "Без категории"
                if transaction.category_id and transaction.category_id in category_dict:
                    category_name = category_dict[transaction.category_id].name
                
                if category_name not in category_stats:
                    category_stats[category_name] = {'income': 0, 'expenses': 0, 'count': 0}
                
                if transaction.transaction_type == TransactionType.INCOME:
                    category_stats[category_name]['income'] += float(transaction.amount)
                else:
                    category_stats[category_name]['expenses'] += float(transaction.amount)
                
                category_stats[category_name]['count'] += 1
            
            # Создаем таблицу по категориям
            category_data = [['Категория', 'Доходы', 'Расходы', 'Чистый результат', 'Количество']]
            
            for category_name, stats in sorted(category_stats.items()):
                net = stats['income'] - stats['expenses']
                category_data.append([
                    category_name,
                    f'{stats["income"]:,.2f} ₽',
                    f'{stats["expenses"]:,.2f} ₽',
                    f'{net:,.2f} ₽',
                    str(stats['count'])
                ])
            
            category_table = Table(category_data)
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(category_table)
        
        # Строим PDF
        doc.build(story)
        
        return str(filepath)
    
    def _generate_summary_data(self, transactions: List[Transaction],
                              categories: List[Category] = None,
                              budgets: List[Budget] = None) -> List[Dict[str, Any]]:
        """
        Генерирует сводные данные для экспорта
        
        Args:
            transactions: Список транзакций
            categories: Список категорий
            budgets: Список бюджетов
        
        Returns:
            Список словарей с сводными данными
        """
        summary_data = []
        
        # Общая статистика
        total_income = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.INCOME)
        total_expenses = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.EXPENSE)
        net_income = total_income - total_expenses
        
        summary_data.extend([
            {'Показатель': 'Общие доходы', 'Значение': f'{total_income:,.2f} ₽', 'Описание': 'Сумма всех доходных транзакций'},
            {'Показатель': 'Общие расходы', 'Значение': f'{total_expenses:,.2f} ₽', 'Описание': 'Сумма всех расходных транзакций'},
            {'Показатель': 'Чистый доход', 'Значение': f'{net_income:,.2f} ₽', 'Описание': 'Разность между доходами и расходами'},
            {'Показатель': 'Количество транзакций', 'Значение': str(len(transactions)), 'Описание': 'Общее количество транзакций'},
            {'Показатель': 'Средняя транзакция', 'Значение': f'{sum(float(t.amount) for t in transactions) / len(transactions):,.2f} ₽', 'Описание': 'Средняя сумма транзакции'},
        ])
        
        # Статистика по категориям
        if categories:
            summary_data.append({'Показатель': 'Количество категорий', 'Значение': str(len(categories)), 'Описание': 'Общее количество категорий'})
        
        # Статистика по бюджетам
        if budgets:
            active_budgets = [b for b in budgets if b.is_active]
            summary_data.append({'Показатель': 'Количество бюджетов', 'Значение': str(len(budgets)), 'Описание': 'Общее количество бюджетов'})
            summary_data.append({'Показатель': 'Активных бюджетов', 'Значение': str(len(active_budgets)), 'Описание': 'Количество активных бюджетов'})
        
        # Период данных
        if transactions:
            min_date = min(t.date.date() for t in transactions)
            max_date = max(t.date.date() for t in transactions)
            summary_data.append({'Показатель': 'Период данных', 'Значение': f'{min_date.strftime("%d.%m.%Y")} - {max_date.strftime("%d.%m.%Y")}', 'Описание': 'Диапазон дат транзакций'})
        
        return summary_data
    
    def export_all_formats(self, transactions: List[Transaction],
                          categories: List[Category] = None,
                          budgets: List[Budget] = None) -> Dict[str, str]:
        """
        Экспорт данных во всех поддерживаемых форматах
        
        Args:
            transactions: Список транзакций
            categories: Список категорий
            budgets: Список бюджетов
        
        Returns:
            Словарь с путями к созданным файлам
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        files = {}
        
        # CSV экспорт
        csv_file = self.export_to_csv(transactions, categories, f"transactions_{timestamp}.csv")
        files['csv'] = csv_file
        
        # Excel экспорт
        excel_file = self.export_to_excel(transactions, categories, budgets, f"finance_{timestamp}.xlsx")
        files['excel'] = excel_file
        
        # PDF экспорт
        pdf_file = self.export_to_pdf(transactions, categories, budgets, f"report_{timestamp}.pdf")
        files['pdf'] = pdf_file
        
        return files
