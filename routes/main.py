"""Dashboard and home redirect."""
from datetime import datetime, timedelta, time
from decimal import Decimal

from flask import Blueprint, redirect, render_template, url_for
from sqlalchemy import func

from models import Category, Employee, Product, Sale, Supplier, db
from utils import login_required

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return redirect(url_for("main.dashboard"))


@bp.route("/dashboard")
@login_required
def dashboard():
    total_products = Product.query.count()
    total_sales_result = db.session.scalar(
        db.select(func.coalesce(func.sum(Sale.total_amount), 0))
    )
    total_sales = total_sales_result if total_sales_result is not None else Decimal("0")
    total_employees = Employee.query.count()
    total_suppliers = Supplier.query.count()

    # Simple chart data: sales per day for last 7 days
    today = datetime.utcnow().date()
    labels = []
    amounts = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime("%b %d"))
        start = datetime.combine(day, time.min)
        end = datetime.combine(day, time.max)
        day_sum = db.session.scalar(
            db.select(func.coalesce(func.sum(Sale.total_amount), 0)).where(
                Sale.created_at >= start, Sale.created_at <= end
            )
        )
        amounts.append(float(day_sum or 0))

    # Products per category for a second chart
    cat_rows = (
        db.session.query(Category.name, func.count(Product.id))
        .outerjoin(Product, Product.category_id == Category.id)
        .group_by(Category.id)
        .all()
    )
    cat_labels = [r[0] for r in cat_rows]
    cat_counts = [r[1] for r in cat_rows]

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_sales=total_sales,
        total_employees=total_employees,
        total_suppliers=total_suppliers,
        chart_labels=labels,
        chart_amounts=amounts,
        cat_labels=cat_labels,
        cat_counts=cat_counts,
    )
