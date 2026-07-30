import os
from datetime import date
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from db import get_db_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")


# ---------- Helper: login required decorator ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------- Auth Routes ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already registered. Please log in.", "warning")
                return redirect(url_for("login"))

            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password),
            )
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------- Dashboard ----------
@app.route("/")
@login_required
def dashboard():
    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date DESC, id DESC",
            (user_id,),
        )
        transactions = cursor.fetchall()

        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = %s AND type = 'income'",
            (user_id,),
        )
        total_income = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = %s AND type = 'expense'",
            (user_id,),
        )
        total_expense = cursor.fetchone()["total"]
    finally:
        cursor.close()
        conn.close()

    balance = float(total_income) - float(total_expense)

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
    )


# ---------- Add Transaction ----------
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        t_type = request.form.get("type")
        category = request.form.get("category", "").strip()
        amount = request.form.get("amount")
        description = request.form.get("description", "").strip()
        transaction_date = request.form.get("transaction_date") or date.today().isoformat()

        if t_type not in ("income", "expense") or not category or not amount:
            flash("Please fill all required fields correctly.", "danger")
            return redirect(url_for("add_transaction"))

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "danger")
            return redirect(url_for("add_transaction"))

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO transactions (user_id, type, category, amount, description, transaction_date)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (session["user_id"], t_type, category, amount, description, transaction_date),
            )
            conn.commit()
            flash("Transaction added successfully.", "success")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_transaction.html", today=date.today().isoformat())


# ---------- Edit Transaction ----------
@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM transactions WHERE id = %s AND user_id = %s",
            (transaction_id, session["user_id"]),
        )
        transaction = cursor.fetchone()

        if not transaction:
            flash("Transaction not found.", "danger")
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            t_type = request.form.get("type")
            category = request.form.get("category", "").strip()
            amount = request.form.get("amount")
            description = request.form.get("description", "").strip()
            transaction_date = request.form.get("transaction_date")

            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                flash("Amount must be a positive number.", "danger")
                return redirect(url_for("edit_transaction", transaction_id=transaction_id))

            update_cursor = conn.cursor()
            try:
                update_cursor.execute(
                    """UPDATE transactions
                       SET type=%s, category=%s, amount=%s, description=%s, transaction_date=%s
                       WHERE id=%s AND user_id=%s""",
                    (t_type, category, amount, description, transaction_date,
                     transaction_id, session["user_id"]),
                )
                conn.commit()
            finally:
                update_cursor.close()

            flash("Transaction updated successfully.", "success")
            return redirect(url_for("dashboard"))
    finally:
        cursor.close()
        conn.close()

    return render_template("edit_transaction.html", transaction=transaction)


# ---------- Delete Transaction ----------
@app.route("/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM transactions WHERE id = %s AND user_id = %s",
            (transaction_id, session["user_id"]),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    flash("Transaction deleted.", "info")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
