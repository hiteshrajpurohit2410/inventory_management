"""Sales / billing: create bills, history, invoice view."""
from collections import defaultdict
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import Product, Sale, SaleLineItem, db
from utils import login_required

bp = Blueprint("sales", __name__, url_prefix="/sales")


def _parse_line_items(form):
    """Build dict product_id -> quantity from form lists."""
    ids = form.getlist("product_id")
    qtys = form.getlist("quantity")
    merged = defaultdict(int)
    for pid, q in zip(ids, qtys):
        if not pid:
            continue
        try:
            product_id = int(pid)
            quantity = int(q)
        except (TypeError, ValueError):
            raise ValueError("Invalid product or quantity in line items.")
        if quantity <= 0:
            continue
        merged[product_id] += quantity
    return dict(merged)


@bp.route("/")
@login_required
def list_sales():
    rows = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template("sales/list.html", sales=rows)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_sale():
    products = Product.query.order_by(Product.name).all()
    if request.method == "POST":
        try:
            lines = _parse_line_items(request.form)
        except ValueError as e:
            flash(str(e), "error")
            return render_template("sales/form.html", products=products)
        if not lines:
            flash("Add at least one product with quantity greater than zero.", "error")
            return render_template("sales/form.html", products=products)

        line_totals = []
        total = Decimal("0.00")
        product_objs = {}

        for product_id, qty in lines.items():
            p = db.session.get(Product, product_id)
            if p is None:
                flash(f"Product ID {product_id} not found.", "error")
                return render_template("sales/form.html", products=products)
            if p.quantity < qty:
                flash(
                    f'Not enough stock for "{p.name}". Available: {p.quantity}, requested: {qty}.',
                    "error",
                )
                return render_template("sales/form.html", products=products)
            unit = Decimal(p.price)
            line_total = (unit * qty).quantize(Decimal("0.01"))
            total += line_total
            line_totals.append((p, qty, unit, line_total))
            product_objs[product_id] = p

        try:
            sale = Sale(
                invoice_number=None,
                total_amount=total.quantize(Decimal("0.01")),
            )
            db.session.add(sale)
            db.session.flush()

            sale.invoice_number = f"INV-{sale.id:06d}"

            for p, qty, unit, line_total in line_totals:
                li = SaleLineItem(
                    sale_id=sale.id,
                    product_id=p.id,
                    quantity=qty,
                    unit_price=unit,
                    line_total=line_total,
                )
                db.session.add(li)
                p.quantity -= qty

            db.session.commit()
            flash(f"Bill {sale.invoice_number} created successfully.", "success")
            return redirect(url_for("sales.invoice", sale_id=sale.id))
        except Exception as exc:
            db.session.rollback()
            flash(f"Could not complete sale: {exc}", "error")
            return render_template("sales/form.html", products=products)

    return render_template("sales/form.html", products=products)


@bp.route("/<int:sale_id>/invoice")
@login_required
def invoice(sale_id):
    sale = db.session.get(Sale, sale_id)
    if sale is None:
        flash("Sale not found.", "error")
        return redirect(url_for("sales.list_sales"))
    return render_template("sales/invoice.html", sale=sale)
