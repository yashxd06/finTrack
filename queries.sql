-- ============================================================
--  ANALYTICAL SQL QUERIES — Personal Finance Tracker
--  These are the exact strings used in app.py (raw SQL).
--  Replace :user_id with the actual parameter binding.
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- QUERY 1: Monthly Income vs Expense
--   Groups all transactions for a user by YYYY-MM,
--   pivoting Income and Expense into separate columns.
-- ────────────────────────────────────────────────────────────
SELECT
    strftime('%Y-%m', t.date)                              AS month,
    COALESCE(SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE 0 END), 0) AS total_income,
    COALESCE(SUM(CASE WHEN c.type = 'Expense' THEN t.amount ELSE 0 END), 0) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
WHERE t.user_id = :user_id
GROUP BY strftime('%Y-%m', t.date)
ORDER BY month ASC;


-- ────────────────────────────────────────────────────────────
-- QUERY 2: Category-Wise Expense Breakdown
--   Joins Transactions + Categories, filters only Expense rows
--   for a specific user, groups by category name.
-- ────────────────────────────────────────────────────────────
SELECT
    c.name                  AS category,
    SUM(t.amount)           AS total_spent
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
WHERE t.user_id    = :user_id
  AND c.type       = 'Expense'
GROUP BY c.category_id, c.name
ORDER BY total_spent DESC;


-- ────────────────────────────────────────────────────────────
-- QUERY 3: Savings Tracking  (Net = Income − Expense)
--   Returns a single row with gross income, gross expense,
--   and the computed net savings for a user.
-- ────────────────────────────────────────────────────────────
SELECT
    COALESCE(SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE 0 END), 0)  AS gross_income,
    COALESCE(SUM(CASE WHEN c.type = 'Expense' THEN t.amount ELSE 0 END), 0)  AS gross_expense,
    COALESCE(SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE 0 END), 0)
  - COALESCE(SUM(CASE WHEN c.type = 'Expense' THEN t.amount ELSE 0 END), 0)  AS net_savings
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
WHERE t.user_id = :user_id;


-- ────────────────────────────────────────────────────────────
-- QUERY 4: Recent Transactions (Dashboard table)
--   Latest 50 transactions with category name & type joined in.
-- ────────────────────────────────────────────────────────────
SELECT
    t.transaction_id,
    t.date,
    t.description,
    t.amount,
    c.name  AS category,
    c.type  AS category_type
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
WHERE t.user_id = :user_id
ORDER BY t.date DESC, t.transaction_id DESC
LIMIT 50;
