-- ============================================================
--  PERSONAL FINANCE TRACKER — DATABASE SCHEMA & SEED DATA
--  Pure SQLite DDL + DML. No ORM. Raw SQL only.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- TABLE 1: Users
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name      VARCHAR(100)  NOT NULL,
    email     VARCHAR(150)  NOT NULL UNIQUE,
    password  VARCHAR(255)  NOT NULL,         -- SHA-256 hex in app.py
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- TABLE 2: Categories
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(80) NOT NULL,
    type        VARCHAR(10) NOT NULL CHECK(type IN ('Income', 'Expense'))
);

-- ------------------------------------------------------------
-- TABLE 3: Transactions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    category_id    INTEGER NOT NULL,
    amount         REAL    NOT NULL CHECK(amount > 0),
    description    TEXT,
    date           DATE    NOT NULL,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)     REFERENCES users(user_id)          ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
);

-- ============================================================
--  SEED DATA
-- ============================================================

-- Users  (passwords are SHA-256 of "password123")
INSERT INTO users (name, email, password) VALUES
    ('Alice Sharma',  'alice@example.com',  'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
    ('Bob Mendes',    'bob@example.com',    'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f');

-- Categories
INSERT INTO categories (name, type) VALUES
    ('Salary',        'Income'),
    ('Freelance',     'Income'),
    ('Investments',   'Income'),
    ('Food & Dining', 'Expense'),
    ('Rent',          'Expense'),
    ('Utilities',     'Expense'),
    ('Transport',     'Expense'),
    ('Healthcare',    'Expense'),
    ('Entertainment', 'Expense'),
    ('Shopping',      'Expense');

-- Transactions for Alice (user_id = 1) — last 4 months
INSERT INTO transactions (user_id, category_id, amount, description, date) VALUES
    -- January
    (1, 1, 85000.00, 'Monthly salary',           '2025-01-01'),
    (1, 2, 12000.00, 'Logo design project',       '2025-01-10'),
    (1, 4,  4200.00, 'Grocery run',               '2025-01-05'),
    (1, 5, 18000.00, 'House rent',                '2025-01-01'),
    (1, 6,  2100.00, 'Electricity & broadband',   '2025-01-15'),
    (1, 7,  1800.00, 'Ola / Metro commute',       '2025-01-20'),
    (1, 9,  3500.00, 'Netflix + concert tickets', '2025-01-25'),
    -- February
    (1, 1, 85000.00, 'Monthly salary',            '2025-02-01'),
    (1, 3,  6000.00, 'Mutual fund dividend',      '2025-02-12'),
    (1, 4,  5100.00, 'Dining out + groceries',    '2025-02-08'),
    (1, 5, 18000.00, 'House rent',                '2025-02-01'),
    (1, 6,  1950.00, 'Electricity bill',          '2025-02-14'),
    (1, 8,  2800.00, 'Doctor visit + medicines',  '2025-02-18'),
    (1,10,  7200.00, 'Clothes shopping',          '2025-02-22'),
    -- March
    (1, 1, 85000.00, 'Monthly salary',            '2025-03-01'),
    (1, 2, 20000.00, 'App development contract',  '2025-03-15'),
    (1, 4,  4600.00, 'Grocery run',               '2025-03-07'),
    (1, 5, 18000.00, 'House rent',                '2025-03-01'),
    (1, 6,  2300.00, 'Broadband + gas',           '2025-03-16'),
    (1, 7,  2100.00, 'Fuel & parking',            '2025-03-20'),
    (1, 9,  1500.00, 'Movie nights',              '2025-03-28'),
    (1,10,  3400.00, 'Amazon shopping',           '2025-03-29'),
    -- April
    (1, 1, 85000.00, 'Monthly salary',            '2025-04-01'),
    (1, 4,  3900.00, 'Groceries',                 '2025-04-03'),
    (1, 5, 18000.00, 'House rent',                '2025-04-01'),
    (1, 7,  1600.00, 'Auto rickshaw + metro',     '2025-04-10'),
    (1, 8,  1200.00, 'Pharmacy',                  '2025-04-12');
