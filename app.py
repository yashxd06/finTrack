"""
app.py — Personal Finance Tracker
Flask backend using raw SQLite3 SQL (no ORM).
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash, g
)

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

DATABASE = os.path.join(os.path.dirname(__file__), "finance.db")


# ─────────────────────────────────────────────
# Database helpers (raw sqlite3, no ORM)
# ─────────────────────────────────────────────
def get_db():
    """Return a per-request DB connection stored on Flask's g object."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row   # rows behave like dicts
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables and seed data from schema.sql (runs once)."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with app.app_context():
        db = get_db()
        with open(schema_path, "r") as f:
            db.executescript(f.read())
        db.commit()


# ─────────────────────────────────────────────
# Auth helpers
# ─────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        password = hash_password(request.form["password"])

        # RAW SQL — intentional, no ORM
        db   = get_db()
        user = db.execute(
            "SELECT user_id, name, email FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        if user:
            session["user_id"]   = user["user_id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form["name"].strip()
        email    = request.form["email"].strip().lower()
        password = hash_password(request.form["password"])

        db = get_db()
        # Check uniqueness first (UNIQUE constraint would also catch it)
        exists = db.execute(
            "SELECT 1 FROM users WHERE email = ?", (email,)
        ).fetchone()

        if exists:
            flash("An account with that email already exists.", "error")
        else:
            # RAW INSERT
            db.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            db.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    db      = get_db()
    user_id = session["user_id"]

    # ── Recent transactions (Query 4) ──
    recent_txns = db.execute("""
        SELECT
            t.transaction_id,
            t.date,
            t.description,
            t.amount,
            c.name  AS category,
            c.type  AS category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = ?
        ORDER BY t.date DESC, t.transaction_id DESC
        LIMIT 50
    """, (user_id,)).fetchall()

    # ── All categories for the "Add Transaction" form ──
    categories = db.execute(
        "SELECT category_id, name, type FROM categories ORDER BY type, name"
    ).fetchall()

    return render_template("dashboard.html",
                           transactions=recent_txns,
                           categories=categories)


# ─────────────────────────────────────────────
# TRANSACTION CRUD
# ─────────────────────────────────────────────
@app.route("/transactions/add", methods=["POST"])
@login_required
def add_transaction():
    user_id     = session["user_id"]
    category_id = int(request.form["category_id"])
    amount      = float(request.form["amount"])
    description = request.form.get("description", "").strip()
    date        = request.form["date"]

    db = get_db()
    # RAW INSERT
    db.execute("""
        INSERT INTO transactions (user_id, category_id, amount, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, category_id, amount, description, date))
    db.commit()
    flash("Transaction added.", "success")
    return redirect(url_for("dashboard"))


@app.route("/transactions/edit/<int:txn_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(txn_id):
    db      = get_db()
    user_id = session["user_id"]

    # Fetch the transaction (ensure it belongs to this user)
    txn = db.execute("""
        SELECT t.*, c.type AS category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.transaction_id = ? AND t.user_id = ?
    """, (txn_id, user_id)).fetchone()

    if not txn:
        flash("Transaction not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        category_id = int(request.form["category_id"])
        amount      = float(request.form["amount"])
        description = request.form.get("description", "").strip()
        date        = request.form["date"]

        # RAW UPDATE
        db.execute("""
            UPDATE transactions
            SET category_id = ?, amount = ?, description = ?, date = ?
            WHERE transaction_id = ? AND user_id = ?
        """, (category_id, amount, description, date, txn_id, user_id))
        db.commit()
        flash("Transaction updated.", "success")
        return redirect(url_for("dashboard"))

    categories = db.execute(
        "SELECT category_id, name, type FROM categories ORDER BY type, name"
    ).fetchall()
    return render_template("edit_transaction.html", txn=txn, categories=categories)


@app.route("/transactions/delete/<int:txn_id>", methods=["POST"])
@login_required
def delete_transaction(txn_id):
    db      = get_db()
    user_id = session["user_id"]

    # RAW DELETE (scoped to user)
    db.execute(
        "DELETE FROM transactions WHERE transaction_id = ? AND user_id = ?",
        (txn_id, user_id)
    )
    db.commit()
    flash("Transaction deleted.", "success")
    return redirect(url_for("dashboard"))


# ─────────────────────────────────────────────
# ANALYTICS API  (returns JSON for Chart.js)
# ─────────────────────────────────────────────
@app.route("/api/analytics")
@login_required
def analytics():
    db      = get_db()
    user_id = session["user_id"]

    # ── Query 1: Monthly Income vs Expense ──
    monthly_rows = db.execute("""
        SELECT
            strftime('%Y-%m', t.date)                                              AS month,
            COALESCE(SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN c.type = 'Expense' THEN t.amount ELSE 0 END), 0) AS total_expense
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = ?
        GROUP BY strftime('%Y-%m', t.date)
        ORDER BY month ASC
    """, (user_id,)).fetchall()

    # ── Query 2: Category-Wise Expense Breakdown ──
    category_rows = db.execute("""
        SELECT
            c.name          AS category,
            SUM(t.amount)   AS total_spent
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = ?
          AND c.type    = 'Expense'
        GROUP BY c.category_id, c.name
        ORDER BY total_spent DESC
    """, (user_id,)).fetchall()

    # ── Query 3: Savings / Net Summary ──
    savings_row = db.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE 0 END), 0)  AS gross_income,
            COALESCE(SUM(CASE WHEN c.type = 'Expense' THEN t.amount ELSE 0 END), 0)  AS gross_expense,
            COALESCE(SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE 0 END), 0)
          - COALESCE(SUM(CASE WHEN c.type = 'Expense' THEN t.amount ELSE 0 END), 0)  AS net_savings
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = ?
    """, (user_id,)).fetchone()

    return jsonify({
        "monthly": [
            {
                "month":         row["month"],
                "total_income":  row["total_income"],
                "total_expense": row["total_expense"]
            }
            for row in monthly_rows
        ],
        "categories": [
            {
                "category":    row["category"],
                "total_spent": row["total_spent"]
            }
            for row in category_rows
        ],
        "savings": {
            "gross_income":  savings_row["gross_income"],
            "gross_expense": savings_row["gross_expense"],
            "net_savings":   savings_row["net_savings"]
        }
    })


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        print("Initialising database from schema.sql …")
        init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
