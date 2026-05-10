
# Inventory Management System

A beginner-friendly portfolio project: session-based authentication, CRUD modules for employees, suppliers, categories, and products, plus multi-line billing with SQLite/SQLAlchemy and an invoice view.

## Tech stack

- **Frontend:** HTML, CSS (responsive layout), Chart.js on the dashboard (CDN)
- **Backend:** Python 3, Flask
- **Database:** SQLite via Flask-SQLAlchemy (ORM)

## Prerequisites

- Python 3.10+ recommended
- `pip` (bundled with Python on Windows if “Add to PATH” was selected)

## Database setup

1. No manual schema creation is required. On first run, the app creates **`inventory.db`** in the project root (see `config.py` → `SQLALCHEMY_DATABASE_URI`).
2. Tables are created automatically with `db.create_all()` inside `create_app()`.
3. If no user exists, a default account is created:
   - **Username:** `admin`
   - **Password:** `admin123`  
   Override with environment variables **`ADMIN_USERNAME`** and **`ADMIN_PASSWORD`** before the first run if you prefer different credentials.
4. To reset the database completely: stop the app, delete `inventory.db`, and start again (a new file and default user will be created).

## How to run

From the project directory:

```bash
# Install dependencies
pip install -r requirements.txt

# Option A — Flask CLI
flask --app app run --debug

# Option B — Direct Python
python app.py
```

Open **http://127.0.0.1:5000** in your browser. Log in with the default user (or your env-configured admin).

For production, set a strong **`SECRET_KEY`** environment variable and never use the default admin password.

## Project layout

| Path | Purpose |
|------|---------|
| `app.py` | Flask app factory, blueprint registration, DB init, default user seed |
| `config.py` | `SECRET_KEY`, SQLite URI |
| `models.py` | SQLAlchemy models (`User`, `Employee`, `Supplier`, `Category`, `Product`, `Sale`, `SaleLineItem`) |
| `utils.py` | `@login_required`, `current_user()` |
| `routes/` | Blueprints: `auth`, `main` (dashboard), `employees`, `suppliers`, `categories`, `products`, `sales` |
| `templates/` | Jinja2 HTML |
| `static/css/style.css` | UI styles |

## Features overview

- **Auth:** Login/logout, hashed passwords (`werkzeug.security`), flash messages on failure.
- **Dashboard:** Counts for products, revenue (sum of sales), employees, suppliers; Chart.js bar chart (7-day sales) and doughnut (products per category).
- **CRUD:** Employees, suppliers, categories, products with validation and dependency checks (e.g. cannot delete a supplier/category still in use).
- **Sales:** Multiple lines per bill; totals computed server-side; stock reduced after commit; invoice page with print-friendly styling.

## Relationships

- **Product → Category / Supplier:** many-to-one each.
- **Sale ↔ Product:** many-to-many implemented with **`SaleLineItem`** (stores quantity and prices at sale time).

# inventory_management
Inventory Management System using Python, Flask and MySQL for product management and CRUD operations.

