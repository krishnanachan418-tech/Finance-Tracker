# 💰 Finance Tracker Application

A full-stack finance tracking web app built with **Python, Flask, MySQL, HTML, CSS**. Users can register, log in, and manage their income & expense transactions with a clean dashboard.

## Features
- User registration & login (passwords hashed with Werkzeug)
- Add / Edit / Delete income & expense transactions
- Dashboard with total income, total expense, and balance
- MySQL database integration
- Session-based authentication

## Tech Stack
- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS

## Project Structure
```
finance-tracker/
├── app.py                 # Main Flask application (routes/logic)
├── db.py                  # MySQL connection helper
├── schema.sql              # Database schema
├── requirements.txt
├── .env.example
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_transaction.html
│   └── edit_transaction.html
└── static/
    └── css/style.css
```

## Setup Instructions (Local)

### 1. Clone / open the project folder
```bash
cd finance-tracker
```

### 2. Create virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up MySQL database
Open MySQL and run:
```bash
mysql -u root -p < schema.sql
```
This creates the `finance_tracker` database with `users` and `transactions` tables.

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your MySQL credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```
SECRET_KEY=your_random_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=finance_tracker
```

### 5. Run the app
```bash
python app.py
```
Visit **http://127.0.0.1:5000** in your browser.

## Deploying to GitHub

Run these commands inside the `finance-tracker` folder:

```bash
git init
git add .
git commit -m "Initial commit - Finance Tracker App"
git branch -M main
git remote add origin https://github.com/<your-username>/finance-tracker.git
git push -u origin main
```

Replace `<your-username>` with your actual GitHub username. Make sure you've created an empty repository named `finance-tracker` on GitHub first (no README/license, so it doesn't conflict with the push).

> ⚠️ Note: `.env` is already excluded via `.gitignore` — never commit your real database password to GitHub.

## Live Deployment (Optional)
To deploy publicly, you can use platforms like **Render**, **Railway**, or **PythonAnywhere**, which support Flask + MySQL. You'll need to:
1. Push code to GitHub (as above)
2. Connect the repo to the hosting platform
3. Set the same environment variables (`SECRET_KEY`, `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) in the platform's dashboard
4. Use a cloud MySQL database (e.g., Railway MySQL, PlanetScale, or Aiven) since local MySQL won't be accessible online

## Author
Krishna Nachan
