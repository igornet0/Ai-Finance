"""
Главный CLI модуль для финансового калькулятора
"""

import click
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from datetime import datetime, date, timedelta
from decimal import Decimal

from ..data.database.initializer import DatabaseInitializer
from ..services import TransactionService, CategoryService, BudgetService, UserService
from ..core.models.transaction import Transaction, TransactionType
from ..core.models.category import Category, CategoryType
from ..core.models.budget import Budget, BudgetPeriod
from ..core.calculators import BalanceCalculator, StatisticsCalculator
from ..analytics import ChartGenerator, ReportGenerator
from ..data.import_export import DataExporter, DataImporter

console = Console()

# Глобальные переменные для сервисов
_services = {}


def get_services():
    """Получает инициализированные сервисы"""
    global _services
    if not _services:
        # Инициализируем базу данных и сервисы
        db_initializer = DatabaseInitializer()
        db_initializer.initialize_database()
        
        _services = {
            'db_initializer': db_initializer,
            'transaction_service': db_initializer.transaction_service,
            'category_service': db_initializer.category_service,
            'budget_service': db_initializer.budget_service,
            'user_service': db_initializer.user_service
        }
    return _services


@click.group()
@click.version_option(version="0.1.0", prog_name="AI Finance")
def main():
    """
    🏦 AI Finance - Личный финансовый калькулятор
    
    Управляйте своими финансами с помощью этого мощного инструмента.
    """
    # Красивый заголовок
    title = Text("🏦 AI Finance", style="bold blue")
    subtitle = Text("Личный финансовый калькулятор", style="italic")
    
    panel = Panel.fit(
        f"{title}\n{subtitle}",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    
    # Инициализируем сервисы
    get_services()


@main.command()
@click.option('--amount', '-a', type=float, required=True, help='Сумма транзакции')
@click.option('--category', '-c', type=str, required=True, help='Категория транзакции')
@click.option('--description', '-d', type=str, help='Описание транзакции')
@click.option('--type', '-t', type=click.Choice(['income', 'expense']), required=True, help='Тип транзакции')
@click.option('--date', type=str, help='Дата транзакции (YYYY-MM-DD), по умолчанию сегодня')
def add_transaction(amount, category, description, type, date):
    """Добавить новую транзакцию"""
    services = get_services()
    transaction_service = services['transaction_service']
    category_service = services['category_service']
    
    try:
        # Находим категорию по имени
        categories = category_service.search_categories(category)
        if not categories:
            console.print(f"❌ Категория '{category}' не найдена")
            return
        
        category_obj = categories[0]  # Берем первую найденную
        
        # Парсим дату
        if date:
            transaction_date = datetime.fromisoformat(date)
        else:
            transaction_date = datetime.now()
        
        # Создаем транзакцию
        transaction = Transaction(
            amount=Decimal(str(amount)),
            transaction_type=TransactionType(type),
            category_id=category_obj.id,
            description=description or '',
            date=transaction_date
        )
        
        # Сохраняем транзакцию
        created_transaction = transaction_service.create_transaction(transaction)
        
        console.print(f"✅ Добавлена транзакция: {type} {amount} руб. в категории '{category_obj.name}'")
        console.print(f"   ID: {created_transaction.id}")
        if description:
            console.print(f"   Описание: {description}")
        console.print(f"   Дата: {transaction_date.strftime('%d.%m.%Y %H:%M')}")
        
    except Exception as e:
        console.print(f"❌ Ошибка при добавлении транзакции: {e}")


@main.command()
@click.option('--period', '-p', type=click.Choice(['day', 'week', 'month', 'year']), 
              default='month', help='Период для отчета')
@click.option('--year', type=int, help='Год для отчета')
@click.option('--month', type=int, help='Месяц для отчета (1-12)')
def report(period, year, month):
    """Показать финансовый отчет"""
    services = get_services()
    transaction_service = services['transaction_service']
    statistics_calculator = StatisticsCalculator()
    
    try:
        # Определяем период
        today = date.today()
        if period == 'day':
            start_date = end_date = today
        elif period == 'week':
            start_date = today.replace(day=today.day - today.weekday())
            end_date = start_date.replace(day=start_date.day + 6)
        elif period == 'month':
            if year and month:
                start_date = date(year, month, 1)
                if month == 12:
                    end_date = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = date(year, month + 1, 1) - timedelta(days=1)
            else:
                start_date = today.replace(day=1)
                if today.month == 12:
                    end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        elif period == 'year':
            if year:
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)
            else:
                start_date = today.replace(month=1, day=1)
                end_date = today.replace(month=12, day=31)
        
        # Получаем транзакции за период
        transactions = transaction_service.get_transactions(start_date=start_date, end_date=end_date)
        statistics_calculator.add_transactions(transactions)
        
        # Рассчитываем статистику
        summary = statistics_calculator._get_period_summary(start_date, end_date)
        
        # Создаем таблицу отчета
        table = Table(title=f"📊 Финансовый отчет за {period}", box=box.ROUNDED)
        table.add_column("Показатель", style="cyan", no_wrap=True)
        table.add_column("Сумма", style="green", justify="right")
        table.add_column("Количество", style="yellow", justify="right")
        
        table.add_row("💰 Доходы", f"{summary['total_income']:,.2f} ₽", "")
        table.add_row("💸 Расходы", f"{summary['total_expenses']:,.2f} ₽", "")
        table.add_row("📈 Чистый доход", f"{summary['net_income']:,.2f} ₽", "")
        table.add_row("📋 Транзакций", "", str(summary['transaction_count']))
        table.add_row("📊 Средняя транзакция", f"{summary['average_transaction']:,.2f} ₽", "")
        
        console.print(table)
        
        # Показываем период
        console.print(f"\n📅 Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
        
    except Exception as e:
        console.print(f"❌ Ошибка при создании отчета: {e}")


@main.command()
def balance():
    """Показать текущий баланс"""
    services = get_services()
    transaction_service = services['transaction_service']
    balance_calculator = BalanceCalculator()
    
    try:
        # Получаем все транзакции
        transactions = transaction_service.get_transactions()
        balance_calculator.add_transactions(transactions)
        
        # Рассчитываем текущий баланс
        current_balance = balance_calculator.calculate_balance()
        
        # Рассчитываем доходы и расходы за текущий месяц
        today = date.today()
        month_start = today.replace(day=1)
        month_income = balance_calculator.calculate_income(month_start, today)
        month_expenses = balance_calculator.calculate_expenses(month_start, today)
        month_net = balance_calculator.calculate_net_income(month_start, today)
        
        # Создаем таблицу баланса
        table = Table(title="💰 Текущий баланс", box=box.ROUNDED)
        table.add_column("Показатель", style="cyan", no_wrap=True)
        table.add_column("Сумма", style="green", justify="right")
        
        table.add_row("💳 Общий баланс", f"{current_balance:,.2f} ₽")
        table.add_row("", "")  # Пустая строка
        table.add_row("📅 За текущий месяц:", "")
        table.add_row("  💰 Доходы", f"{month_income:,.2f} ₽")
        table.add_row("  💸 Расходы", f"{month_expenses:,.2f} ₽")
        table.add_row("  📈 Чистый доход", f"{month_net:,.2f} ₽")
        
        console.print(table)
        
        # Показываем дату
        console.print(f"\n📅 Дата: {today.strftime('%d.%m.%Y')}")
        
    except Exception as e:
        console.print(f"❌ Ошибка при расчете баланса: {e}")


@main.command()
def budget():
    """Показать статус бюджетов"""
    services = get_services()
    budget_service = services['budget_service']
    
    try:
        # Получаем статус всех активных бюджетов
        budgets_status = budget_service.get_all_budgets_status()
        
        if not budgets_status:
            console.print("📋 Нет активных бюджетов")
            return
        
        # Создаем таблицу бюджетов
        table = Table(title="📋 Статус бюджетов", box=box.ROUNDED)
        table.add_column("Бюджет", style="cyan", no_wrap=True)
        table.add_column("Лимит", style="green", justify="right")
        table.add_column("Потрачено", style="yellow", justify="right")
        table.add_column("Остаток", style="blue", justify="right")
        table.add_column("Использование", style="magenta", justify="right")
        table.add_column("Статус", style="red", justify="center")
        
        for budget_status in budgets_status:
            # Определяем цвет статуса
            if budget_status['is_over_budget']:
                status_icon = "🔴"
            elif budget_status['is_near_limit']:
                status_icon = "🟡"
            else:
                status_icon = "🟢"
            
            table.add_row(
                budget_status['budget_name'],
                f"{budget_status['budget_amount']:,.2f} ₽",
                f"{budget_status['spent_amount']:,.2f} ₽",
                f"{budget_status['remaining_amount']:,.2f} ₽",
                f"{budget_status['usage_percentage']:.1f}%",
                status_icon
            )
        
        console.print(table)
        
        # Показываем предупреждения
        alerts = budget_service.get_budget_alerts()
        if alerts:
            console.print("\n⚠️  Предупреждения:")
            for alert in alerts:
                console.print(f"  • {alert['message']}")
        
    except Exception as e:
        console.print(f"❌ Ошибка при получении статуса бюджетов: {e}")


@main.command()
def categories():
    """Показать список категорий"""
    services = get_services()
    category_service = services['category_service']
    
    try:
        # Получаем все категории
        categories = category_service.get_categories()
        
        if not categories:
            console.print("📁 Нет категорий")
            return
        
        # Создаем таблицу категорий
        table = Table(title="📁 Категории", box=box.ROUNDED)
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Название", style="green")
        table.add_column("Тип", style="yellow")
        table.add_column("Иконка", style="blue", justify="center")
        table.add_column("Активна", style="magenta", justify="center")
        
        for category in categories:
            type_icon = "💰" if category.is_income_category else "💸"
            active_icon = "✅" if category.is_active else "❌"
            
            table.add_row(
                str(category.id),
                category.name,
                type_icon,
                category.icon,
                active_icon
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Ошибка при получении категорий: {e}")


@main.command()
@click.option('--limit', '-l', type=int, default=10, help='Количество последних транзакций')
def transactions(limit):
    """Показать последние транзакции"""
    services = get_services()
    transaction_service = services['transaction_service']
    category_service = services['category_service']
    
    try:
        # Получаем последние транзакции
        transactions = transaction_service.get_transactions(limit=limit)
        
        if not transactions:
            console.print("💳 Нет транзакций")
            return
        
        # Создаем таблицу транзакций
        table = Table(title=f"💳 Последние {limit} транзакций", box=box.ROUNDED)
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Дата", style="blue")
        table.add_column("Тип", style="yellow", justify="center")
        table.add_column("Сумма", style="green", justify="right")
        table.add_column("Категория", style="magenta")
        table.add_column("Описание", style="white")
        
        for transaction in transactions:
            # Получаем категорию
            category_name = "Без категории"
            if transaction.category_id:
                category = category_service.get_category(transaction.category_id)
                if category:
                    category_name = category.name
            
            # Определяем иконку типа
            type_icon = "💰" if transaction.is_income else "💸"
            
            # Форматируем сумму
            amount_str = f"{transaction.amount:,.2f} ₽"
            if transaction.is_expense:
                amount_str = f"-{amount_str}"
            
            table.add_row(
                str(transaction.id),
                transaction.date.strftime('%d.%m.%Y'),
                type_icon,
                amount_str,
                category_name,
                transaction.description[:30] + "..." if len(transaction.description) > 30 else transaction.description
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Ошибка при получении транзакций: {e}")


@main.command()
@click.option('--start-date', type=str, help='Начальная дата (YYYY-MM-DD)')
@click.option('--end-date', type=str, help='Конечная дата (YYYY-MM-DD)')
@click.option('--output-dir', type=str, default='reports', help='Директория для сохранения отчетов')
def generate_report(start_date, end_date, output_dir):
    """Генерировать комплексный финансовый отчет с графиками"""
    services = get_services()
    transaction_service = services['transaction_service']
    category_service = services['category_service']
    budget_service = services['budget_service']
    
    try:
        # Определяем период
        if start_date and end_date:
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()
        else:
            # По умолчанию - текущий месяц
            today = date.today()
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        console.print(f"📊 Генерация отчета за период: {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}")
        
        # Получаем данные
        transactions = transaction_service.get_transactions(start_date=start, end_date=end)
        categories = category_service.get_categories()
        budget_statuses = budget_service.get_all_budgets_status()
        
        if not transactions:
            console.print("❌ Нет транзакций за указанный период")
            return
        
        # Создаем генератор отчетов
        report_generator = ReportGenerator(output_dir)
        
        # Генерируем комплексный отчет
        files = report_generator.generate_comprehensive_report(
            transactions, categories, budget_statuses, start, end
        )
        
        console.print("✅ Отчет успешно создан!")
        console.print(f"📁 Директория: {output_dir}")
        
        # Показываем созданные файлы
        table = Table(title="📋 Созданные файлы", box=box.ROUNDED)
        table.add_column("Тип", style="cyan")
        table.add_column("Файл", style="green")
        
        for file_type, file_path in files.items():
            filename = os.path.basename(file_path)
            table.add_row(file_type, filename)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Ошибка при создании отчета: {e}")


@main.command()
@click.option('--year', type=int, help='Год для отчета')
@click.option('--month', type=int, help='Месяц для отчета (1-12)')
@click.option('--output-dir', type=str, default='reports', help='Директория для сохранения отчетов')
def monthly_report(year, month, output_dir):
    """Генерировать месячный отчет"""
    services = get_services()
    transaction_service = services['transaction_service']
    category_service = services['category_service']
    
    try:
        # Определяем год и месяц
        if not year or not month:
            today = date.today()
            year = year or today.year
            month = month or today.month
        
        console.print(f"📊 Генерация месячного отчета: {month:02d}.{year}")
        
        # Получаем данные
        transactions = transaction_service.get_transactions()
        categories = category_service.get_categories()
        
        if not transactions:
            console.print("❌ Нет транзакций")
            return
        
        # Создаем генератор отчетов
        report_generator = ReportGenerator(output_dir)
        
        # Генерируем месячный отчет
        files = report_generator.generate_monthly_report(
            transactions, categories, year, month
        )
        
        console.print("✅ Месячный отчет успешно создан!")
        console.print(f"📁 Директория: {output_dir}")
        
        # Показываем созданные файлы
        table = Table(title="📋 Созданные файлы", box=box.ROUNDED)
        table.add_column("Тип", style="cyan")
        table.add_column("Файл", style="green")
        
        for file_type, file_path in files.items():
            filename = os.path.basename(file_path)
            table.add_row(file_type, filename)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Ошибка при создании месячного отчета: {e}")


@main.command()
@click.option('--chart-type', type=click.Choice(['balance', 'income-expense', 'category-pie', 'trends', 'budget']), 
              required=True, help='Тип графика')
@click.option('--start-date', type=str, help='Начальная дата (YYYY-MM-DD)')
@click.option('--end-date', type=str, help='Конечная дата (YYYY-MM-DD)')
@click.option('--output-dir', type=str, default='charts', help='Директория для сохранения графиков')
def generate_chart(chart_type, start_date, end_date, output_dir):
    """Генерировать график"""
    services = get_services()
    transaction_service = services['transaction_service']
    budget_service = services['budget_service']
    
    try:
        # Определяем период
        if start_date and end_date:
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()
        else:
            # По умолчанию - последние 30 дней
            end = date.today()
            start = end - timedelta(days=30)
        
        console.print(f"📈 Генерация графика: {chart_type}")
        console.print(f"📅 Период: {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}")
        
        # Получаем данные
        transactions = transaction_service.get_transactions(start_date=start, end_date=end)
        
        if not transactions:
            console.print("❌ Нет транзакций за указанный период")
            return
        
        # Создаем генератор графиков
        chart_generator = ChartGenerator(output_dir)
        
        # Генерируем график в зависимости от типа
        if chart_type == 'balance':
            file_path = chart_generator.generate_balance_chart(transactions, start, end)
        elif chart_type == 'income-expense':
            file_path = chart_generator.generate_income_expense_chart(transactions, start, end)
        elif chart_type == 'category-pie':
            file_path = chart_generator.generate_category_pie_chart(transactions, start, end)
        elif chart_type == 'trends':
            file_path = chart_generator.generate_trend_analysis_chart(transactions)
        elif chart_type == 'budget':
            budget_statuses = budget_service.get_all_budgets_status()
            if not budget_statuses:
                console.print("❌ Нет активных бюджетов")
                return
            file_path = chart_generator.generate_budget_status_chart(budget_statuses)
        
        console.print(f"✅ График успешно создан: {os.path.basename(file_path)}")
        console.print(f"📁 Путь: {file_path}")
        
    except Exception as e:
        console.print(f"❌ Ошибка при создании графика: {e}")


@main.command()
@click.option('--format', 'export_format', type=click.Choice(['csv', 'excel', 'pdf', 'all']), 
              default='all', help='Формат экспорта')
@click.option('--output-dir', type=str, default='exports', help='Директория для сохранения файлов')
def export_data(export_format, output_dir):
    """Экспортировать данные в различных форматах"""
    services = get_services()
    transaction_service = services['transaction_service']
    category_service = services['category_service']
    budget_service = services['budget_service']
    
    try:
        console.print(f"📤 Экспорт данных в формате: {export_format}")
        
        # Получаем данные
        transactions = transaction_service.get_transactions()
        categories = category_service.get_categories()
        budgets = budget_service.get_budgets()
        
        if not transactions:
            console.print("❌ Нет транзакций для экспорта")
            return
        
        # Создаем экспортер
        exporter = DataExporter(output_dir)
        
        # Экспортируем в зависимости от формата
        if export_format == 'csv':
            file_path = exporter.export_to_csv(transactions, categories)
            console.print(f"✅ CSV файл создан: {os.path.basename(file_path)}")
        elif export_format == 'excel':
            file_path = exporter.export_to_excel(transactions, categories, budgets)
            console.print(f"✅ Excel файл создан: {os.path.basename(file_path)}")
        elif export_format == 'pdf':
            file_path = exporter.export_to_pdf(transactions, categories, budgets)
            console.print(f"✅ PDF файл создан: {os.path.basename(file_path)}")
        elif export_format == 'all':
            files = exporter.export_all_formats(transactions, categories, budgets)
            console.print("✅ Все форматы экспортированы!")
            
            # Показываем созданные файлы
            table = Table(title="📋 Созданные файлы", box=box.ROUNDED)
            table.add_column("Формат", style="cyan")
            table.add_column("Файл", style="green")
            
            for format_type, file_path in files.items():
                filename = os.path.basename(file_path)
                table.add_row(format_type.upper(), filename)
            
            console.print(table)
        
        console.print(f"📁 Директория: {output_dir}")
        
    except Exception as e:
        console.print(f"❌ Ошибка при экспорте данных: {e}")


@main.command()
@click.option('--file', 'file_path', type=str, required=True, help='Путь к файлу для импорта')
@click.option('--format', 'import_format', type=click.Choice(['csv', 'excel', 'bank']), 
              default='csv', help='Формат импорта')
@click.option('--date-format', type=str, default='%d.%m.%Y', help='Формат даты в файле')
@click.option('--skip-duplicates', is_flag=True, default=True, help='Пропускать дубликаты')
@click.option('--validate-only', is_flag=True, help='Только валидация файла без импорта')
def import_data(file_path, import_format, date_format, skip_duplicates, validate_only):
    """Импортировать данные из файла"""
    services = get_services()
    transaction_service = services['transaction_service']
    category_service = services['category_service']
    
    try:
        console.print(f"📥 Импорт данных из файла: {os.path.basename(file_path)}")
        console.print(f"📋 Формат: {import_format}")
        
        # Создаем импортер
        importer = DataImporter()
        
        if validate_only:
            # Только валидация
            validation_result = importer.validate_import_file(file_path, import_format)
            
            if validation_result['valid']:
                console.print("✅ Файл валиден!")
                console.print(f"📊 Количество строк: {validation_result['row_count']}")
                console.print(f"📋 Колонки: {', '.join(validation_result['columns'])}")
                
                # Показываем пример данных
                if 'sample_data' in validation_result:
                    table = Table(title="📋 Пример данных", box=box.ROUNDED)
                    if validation_result['sample_data']:
                        # Добавляем колонки
                        for key in validation_result['sample_data'][0].keys():
                            table.add_column(key, style="cyan")
                        
                        # Добавляем строки
                        for row in validation_result['sample_data']:
                            table.add_row(*[str(value) for value in row.values()])
                        
                        console.print(table)
            else:
                console.print(f"❌ Файл невалиден: {validation_result['error']}")
                if 'available_columns' in validation_result:
                    console.print(f"📋 Доступные колонки: {', '.join(validation_result['available_columns'])}")
        else:
            # Импорт данных
            if import_format == 'csv':
                results = importer.import_from_csv(
                    file_path, transaction_service, category_service, 
                    date_format, skip_duplicates
                )
            elif import_format == 'excel':
                results = importer.import_from_excel(
                    file_path, transaction_service, category_service, 
                    skip_duplicates=skip_duplicates
                )
            elif import_format == 'bank':
                results = importer.import_bank_statement(
                    file_path, transaction_service, category_service,
                    skip_duplicates=skip_duplicates
                )
            
            # Показываем результаты
            console.print("✅ Импорт завершен!")
            console.print(f"📥 Импортировано: {results['imported']} транзакций")
            console.print(f"⏭️  Пропущено: {results['skipped']} дубликатов")
            console.print(f"❌ Ошибок: {results['errors']}")
            
            if results['error_details']:
                console.print("\n🔍 Детали ошибок:")
                for error in results['error_details'][:5]:  # Показываем первые 5 ошибок
                    console.print(f"  • {error}")
                if len(results['error_details']) > 5:
                    console.print(f"  ... и еще {len(results['error_details']) - 5} ошибок")
        
    except Exception as e:
        console.print(f"❌ Ошибка при импорте данных: {e}")


@main.command()
def gui():
    """Запустить графический интерфейс"""
    try:
        from ..ui.main_window import MainWindow
        
        console.print("🖥️  Запуск графического интерфейса...")
        
        # Создаем и запускаем главное окно
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        console.print(f"❌ Ошибка импорта GUI модулей: {e}")
        console.print("Убедитесь, что установлены все зависимости для GUI")
    except Exception as e:
        console.print(f"❌ Ошибка при запуске GUI: {e}")


if __name__ == "__main__":
    main()
