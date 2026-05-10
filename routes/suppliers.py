"""Supplier CRUD."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import Supplier, db
from utils import login_required

bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")


@bp.route("/")
@login_required
def list_suppliers():
    rows = Supplier.query.order_by(Supplier.name).all()
    return render_template("suppliers/list.html", suppliers=rows)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        contact = (request.form.get("contact") or "").strip()
        address = (request.form.get("address") or "").strip()
        if not name or not contact or not address:
            flash("Name, contact, and address are required.", "error")
            return render_template("suppliers/form.html", supplier=None)
        s = Supplier(name=name, contact=contact, address=address)
        db.session.add(s)
        db.session.commit()
        flash("Supplier added.", "success")
        return redirect(url_for("suppliers.list_suppliers"))
    return render_template("suppliers/form.html", supplier=None)


@bp.route("/<int:supplier_id>/edit", methods=["GET", "POST"])
@login_required
def edit(supplier_id):
    s = db.session.get(Supplier, supplier_id)
    if s is None:
        flash("Supplier not found.", "error")
        return redirect(url_for("suppliers.list_suppliers"))
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        contact = (request.form.get("contact") or "").strip()
        address = (request.form.get("address") or "").strip()
        if not name or not contact or not address:
            flash("Name, contact, and address are required.", "error")
            return render_template("suppliers/form.html", supplier=s)
        s.name = name
        s.contact = contact
        s.address = address
        db.session.commit()
        flash("Supplier updated.", "success")
        return redirect(url_for("suppliers.list_suppliers"))
    return render_template("suppliers/form.html", supplier=s)


@bp.route("/<int:supplier_id>/delete", methods=["POST"])
@login_required
def delete(supplier_id):
    s = db.session.get(Supplier, supplier_id)
    if s is None:
        flash("Supplier not found.", "error")
    else:
        if s.products:
            flash("Cannot delete supplier that still has products. Reassign products first.", "error")
        else:
            db.session.delete(s)
            db.session.commit()
            flash("Supplier deleted.", "success")
    return redirect(url_for("suppliers.list_suppliers"))
