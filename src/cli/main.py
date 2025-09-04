"""
Главный CLI модуль для финансового калькулятора
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


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


@main.command()
@click.option('--amount', '-a', type=float, required=True, help='Сумма транзакции')
@click.option('--category', '-c', type=str, required=True, help='Категория транзакции')
@click.option('--description', '-d', type=str, help='Описание транзакции')
@click.option('--type', '-t', type=click.Choice(['income', 'expense']), required=True, help='Тип транзакции')
def add_transaction(amount, category, description, type):
    """Добавить новую транзакцию"""
    console.print(f"✅ Добавлена транзакция: {type} {amount} руб. в категории '{category}'")
    if description:
        console.print(f"   Описание: {description}")


@main.command()
@click.option('--period', '-p', type=click.Choice(['day', 'week', 'month', 'year']), 
              default='month', help='Период для отчета')
def report(period):
    """Показать финансовый отчет"""
    console.print(f"📊 Финансовый отчет за {period}")
    console.print("(Функция будет реализована в следующих версиях)")


@main.command()
def balance():
    """Показать текущий баланс"""
    console.print("💰 Текущий баланс")
    console.print("(Функция будет реализована в следующих версиях)")


@main.command()
def budget():
    """Управление бюджетом"""
    console.print("📋 Управление бюджетом")
    console.print("(Функция будет реализована в следующих версиях)")


@main.command()
def gui():
    """Запустить графический интерфейс"""
    console.print("🖥️  Запуск графического интерфейса...")
    console.print("(Функция будет реализована в следующих версиях)")


if __name__ == "__main__":
    main()
