"""Product CRUD."""
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import Category, Product, Supplier, db
from utils import login_required

bp = Blueprint("products", __name__, url_prefix="/products")


def _parse_positive_int(value, field_label):
    try:
        n = int(value)
        if n < 0:
            raise ValueError
        return n
    except (TypeError, ValueError):
        raise ValueError(f"{field_label} must be a non-negative integer.")


def _parse_price(value):
    try:
        d = Decimal(str(value).strip())
        if d < 0:
            raise ValueError
        return d.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as e:
        raise ValueError("Price must be a valid non-negative number.") from e


@bp.route("/")
@login_required
def list_products():
    rows = (
        Product.query.join(Category)
        .join(Supplier)
        .order_by(Product.name)
        .all()
    )
    return render_template("products/list.html", products=rows)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    categories = Category.query.order_by(Category.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        category_id = request.form.get("category_id")
        supplier_id = request.form.get("supplier_id")
        try:
            quantity = _parse_positive_int(request.form.get("quantity"), "Quantity")
            price = _parse_price(request.form.get("price"))
        except ValueError as err:
            flash(str(err), "error")
            return render_template(
                "products/form.html",
                product=None,
                categories=categories,
                suppliers=suppliers,
            )
        if not name:
            flash("Product name is required.", "error")
            return render_template(
                "products/form.html",
                product=None,
                categories=categories,
                suppliers=suppliers,
            )
        cat = db.session.get(Category, int(category_id)) if category_id else None
        sup = db.session.get(Supplier, int(supplier_id)) if supplier_id else None
        if cat is None or sup is None:
            flash("Please select a valid category and supplier.", "error")
            return render_template(
                "products/form.html",
                product=None,
                categories=categories,
                suppliers=suppliers,
            )
        p = Product(
            name=name,
            category_id=cat.id,
            supplier_id=sup.id,
            quantity=quantity,
            price=price,
        )
        db.session.add(p)
        db.session.commit()
        flash("Product added.", "success")
        return redirect(url_for("products.list_products"))
    return render_template(
        "products/form.html",
        product=None,
        categories=categories,
        suppliers=suppliers,
    )


@bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit(product_id):
    p = db.session.get(Product, product_id)
    categories = Category.query.order_by(Category.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    if p is None:
        flash("Product not found.", "error")
        return redirect(url_for("products.list_products"))
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        category_id = request.form.get("category_id")
        supplier_id = request.form.get("supplier_id")
        try:
            quantity = _parse_positive_int(request.form.get("quantity"), "Quantity")
            price = _parse_price(request.form.get("price"))
        except ValueError as err:
            flash(str(err), "error")
            return render_template(
                "products/form.html",
                product=p,
                categories=categories,
                suppliers=suppliers,
            )
        if not name:
            flash("Product name is required.", "error")
            return render_template(
                "products/form.html",
                product=p,
                categories=categories,
                suppliers=suppliers,
            )
        cat = db.session.get(Category, int(category_id)) if category_id else None
        sup = db.session.get(Supplier, int(supplier_id)) if supplier_id else None
        if cat is None or sup is None:
            flash("Please select a valid category and supplier.", "error")
            return render_template(
                "products/form.html",
                product=p,
                categories=categories,
                suppliers=suppliers,
            )
        p.name = name
        p.category_id = cat.id
        p.supplier_id = sup.id
        p.quantity = quantity
        p.price = price
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("products.list_products"))
    return render_template(
        "products/form.html",
        product=p,
        categories=categories,
        suppliers=suppliers,
    )


@bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
def delete(product_id):
    p = db.session.get(Product, product_id)
    if p is None:
        flash("Product not found.", "error")
    elif p.line_items:
        flash("Cannot delete a product that appears on past sales.", "error")
    else:
        db.session.delete(p)
        db.session.commit()
        flash("Product deleted.", "success")
    return redirect(url_for("products.list_products"))
