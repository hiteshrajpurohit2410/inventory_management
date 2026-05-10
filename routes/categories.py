"""Category CRUD."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import Category, db
from utils import login_required

bp = Blueprint("categories", __name__, url_prefix="/categories")


@bp.route("/")
@login_required
def list_categories():
    rows = Category.query.order_by(Category.name).all()
    return render_template("categories/list.html", categories=rows)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Category name is required.", "error")
            return render_template("categories/form.html", category=None)
        if Category.query.filter_by(name=name).first():
            flash("A category with that name already exists.", "error")
            return render_template("categories/form.html", category=None)
        c = Category(name=name)
        db.session.add(c)
        db.session.commit()
        flash("Category added.", "success")
        return redirect(url_for("categories.list_categories"))
    return render_template("categories/form.html", category=None)


@bp.route("/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit(category_id):
    c = db.session.get(Category, category_id)
    if c is None:
        flash("Category not found.", "error")
        return redirect(url_for("categories.list_categories"))
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Category name is required.", "error")
            return render_template("categories/form.html", category=c)
        other = Category.query.filter(Category.name == name, Category.id != category_id).first()
        if other:
            flash("A category with that name already exists.", "error")
            return render_template("categories/form.html", category=c)
        c.name = name
        db.session.commit()
        flash("Category updated.", "success")
        return redirect(url_for("categories.list_categories"))
    return render_template("categories/form.html", category=c)


@bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete(category_id):
    c = db.session.get(Category, category_id)
    if c is None:
        flash("Category not found.", "error")
    else:
        if c.products:
            flash("Cannot delete category that has products. Delete or move products first.", "error")
        else:
            db.session.delete(c)
            db.session.commit()
            flash("Category deleted.", "success")
    return redirect(url_for("categories.list_categories"))
