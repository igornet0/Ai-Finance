#!/usr/bin/env python3
"""
Скрипт для резервного копирования данных AI Finance
"""

import os
import sys
import subprocess
import datetime
import json
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_connection():
    """Получить соединение с базой данных"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/ai_finance')
    return psycopg2.connect(database_url)

def backup_database():
    """Создать резервную копию базы данных"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path('/app/backups')
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f'ai_finance_backup_{timestamp}.sql'
    
    # Извлекаем параметры подключения из DATABASE_URL
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/ai_finance')
    
    # Создаем резервную копию с помощью pg_dump
    cmd = [
        'pg_dump',
        database_url,
        '--verbose',
        '--clean',
        '--no-owner',
        '--no-privileges',
        '--format=plain',
        f'--file={backup_file}'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Резервная копия базы данных создана: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании резервной копии: {e}")
        print(f"stderr: {e.stderr}")
        return None

def backup_data_files():
    """Создать резервную копию файлов данных"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path('/app/backups')
    backup_dir.mkdir(exist_ok=True)
    
    data_dir = Path('/app/data')
    if not data_dir.exists():
        print("⚠️  Директория данных не найдена")
        return None
    
    backup_file = backup_dir / f'data_backup_{timestamp}.tar.gz'
    
    cmd = [
        'tar',
        '-czf',
        str(backup_file),
        '-C',
        str(data_dir.parent),
        'data'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Резервная копия файлов создана: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании резервной копии файлов: {e}")
        return None

def export_transactions_json():
    """Экспортировать транзакции в JSON"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path('/app/backups')
    backup_dir.mkdir(exist_ok=True)
    
    json_file = backup_dir / f'transactions_{timestamp}.json'
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Получаем все транзакции
        cursor.execute("""
            SELECT t.*, c.name as category_name, u.username
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN users u ON t.user_id = u.id
            ORDER BY t.date DESC
        """)
        
        transactions = cursor.fetchall()
        
        # Конвертируем в JSON-совместимый формат
        json_data = []
        for transaction in transactions:
            json_data.append(dict(transaction))
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Экспорт транзакций в JSON: {json_file}")
        return json_file
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте транзакций: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def cleanup_old_backups():
    """Удалить старые резервные копии (старше 30 дней)"""
    backup_dir = Path('/app/backups')
    if not backup_dir.exists():
        return
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
    
    for backup_file in backup_dir.glob('*'):
        if backup_file.is_file():
            file_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff_date:
                backup_file.unlink()
                print(f"🗑️  Удален старый файл: {backup_file}")

def main():
    """Основная функция"""
    print("🚀 Начинаем резервное копирование AI Finance...")
    print(f"📅 Время: {datetime.datetime.now()}")
    
    # Создаем резервные копии
    db_backup = backup_database()
    data_backup = backup_data_files()
    json_export = export_transactions_json()
    
    # Очищаем старые файлы
    cleanup_old_backups()
    
    # Сводка
    print("\n📊 Сводка резервного копирования:")
    if db_backup:
        print(f"  ✅ База данных: {db_backup}")
    if data_backup:
        print(f"  ✅ Файлы данных: {data_backup}")
    if json_export:
        print(f"  ✅ JSON экспорт: {json_export}")
    
    print("🎉 Резервное копирование завершено!")

if __name__ == "__main__":
    main()
