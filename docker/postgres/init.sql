-- Инициализация базы данных AI Finance

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Создание схемы для приложения
CREATE SCHEMA IF NOT EXISTS ai_finance;

-- Установка поискового пути
SET search_path TO ai_finance, public;

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    currency VARCHAR(3) DEFAULT 'RUB',
    timezone VARCHAR(50) DEFAULT 'Europe/Moscow',
    language VARCHAR(5) DEFAULT 'ru',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы категорий
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_type VARCHAR(20) NOT NULL CHECK (category_type IN ('income', 'expense', 'both')),
    parent_id INTEGER REFERENCES categories(id),
    color VARCHAR(7) DEFAULT '#3498db',
    icon VARCHAR(10) DEFAULT '📁',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы транзакций
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('income', 'expense', 'transfer')),
    category_id INTEGER REFERENCES categories(id),
    description TEXT,
    date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    account_id INTEGER,
    tags TEXT[],
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы бюджетов
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    amount DECIMAL(15,2) NOT NULL,
    period VARCHAR(20) NOT NULL CHECK (period IN ('daily', 'weekly', 'monthly', 'yearly')),
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    alert_threshold DECIMAL(3,2) DEFAULT 0.80,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индексов для производительности
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(category_type);
CREATE INDEX IF NOT EXISTS idx_budgets_user ON budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets(category_id);

-- Создание триггеров для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Вставка базовых категорий
INSERT INTO categories (name, category_type, icon, color) VALUES
    ('Зарплата', 'income', '💰', '#2ecc71'),
    ('Фриланс', 'income', '💻', '#2ecc71'),
    ('Инвестиции', 'income', '📈', '#2ecc71'),
    ('Подарки', 'income', '🎁', '#2ecc71'),
    ('Продукты', 'expense', '🛒', '#e74c3c'),
    ('Транспорт', 'expense', '🚗', '#e74c3c'),
    ('Развлечения', 'expense', '🎬', '#e74c3c'),
    ('Здоровье', 'expense', '🏥', '#e74c3c'),
    ('Образование', 'expense', '📚', '#e74c3c'),
    ('Коммунальные', 'expense', '🏠', '#e74c3c'),
    ('Одежда', 'expense', '👕', '#e74c3c'),
    ('Прочее', 'expense', '📦', '#e74c3c')
ON CONFLICT DO NOTHING;

-- Создание пользователя по умолчанию
INSERT INTO users (username, email, full_name) VALUES
    ('admin', 'admin@ai-finance.local', 'Администратор')
ON CONFLICT (username) DO NOTHING;
