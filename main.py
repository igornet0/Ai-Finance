#!/usr/bin/env python3
"""
Главный файл для запуска личного финансового калькулятора.
"""

import sys
import os

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.main import main

if __name__ == "__main__":
    main()
