# FinTrack — Personal Finance Tracker
### SQL-first · Flask · No ORM · Raw sqlite3

---

## Quick Start

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install Flask
pip install -r requirements.txt

# 3. Run the app (auto-creates finance.db from schema.sql on first run)
python app.py
```

Open **http://127.0.0.1:5000**

**Demo credentials:**
- Email: `alice@example.com`
- Password: `password123`

---

## Project Structure

```
finance_tracker/
├── app.py              ← Flask app — all routes, raw sqlite3 SQL
├── schema.sql          ← DDL (CREATE TABLE) + seed data (INSERT)
├── queries.sql         ← Analytical SQL queries (reference)
├── finance.db          ← Auto-generated SQLite database
├── requirements.txt
├── static/
│   ├── css/style.css
│   └── js/dashboard.js ← Chart.js rendering + API fetch
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    └── edit_transaction.html
```

---

## Database Schema

```
users            categories          transactions
─────────────    ──────────────────  ──────────────────────────────
user_id (PK)     category_id (PK)    transaction_id (PK)
name             name                user_id     (FK → users)
email (UNIQUE)   type CHECK(         category_id (FK → categories)
password           'Income'|         amount
created_at         'Expense')        description
                                     date
                                     created_at
```

---

## Analytical SQL Queries

### 1 · Monthly Income vs Expense
```sql
SELECT
    strftime('%Y-%m', t.date)                                              AS month,
    COALESCE(SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE 0 END), 0) AS total_income,
    COALESCE(SUM(CASE WHEN c.type = 'Expense' THEN t.amount ELSE 0 END), 0) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
WHERE t.user_id = :user_id
GROUP BY strftime('%Y-%m', t.date)
ORDER BY month ASC;
```

### 2 · Category-Wise Expense Breakdown
```sql
SELECT
    c.name          AS category,
    SUM(t.amount)   AS total_spent
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
WHERE t.user_id = :user_id  AND  c.type = 'Expense'
GROUP BY c.category_id, c.name
ORDER BY total_spent DESC;
```

### 3 · Savings Tracking
```sql
SELECT
    COALESCE(SUM(CASE WHEN c.type='Income'  THEN t.amount ELSE 0 END),0)  AS gross_income,
    COALESCE(SUM(CASE WHEN c.type='Expense' THEN t.amount ELSE 0 END),0)  AS gross_expense,
    COALESCE(SUM(CASE WHEN c.type='Income'  THEN t.amount ELSE 0 END),0)
  - COALESCE(SUM(CASE WHEN c.type='Expense' THEN t.amount ELSE 0 END),0)  AS net_savings
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
WHERE t.user_id = :user_id;
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET/POST | `/login` | Login page |
| GET/POST | `/register` | Registration page |
| GET | `/logout` | Clear session |
| GET | `/dashboard` | Main dashboard |
| POST | `/transactions/add` | Add transaction |
| GET/POST | `/transactions/edit/<id>` | Edit transaction |
| POST | `/transactions/delete/<id>` | Delete transaction |
| GET | `/api/analytics` | JSON: monthly + category + savings data |
