"""Employee CRUD."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import Employee, db
from utils import login_required

bp = Blueprint("employees", __name__, url_prefix="/employees")


@bp.route("/")
@login_required
def list_employees():
    rows = Employee.query.order_by(Employee.name).all()
    return render_template("employees/list.html", employees=rows)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        role = (request.form.get("role") or "").strip()
        contact = (request.form.get("contact") or "").strip()
        if not name or not role or not contact:
            flash("Name, role, and contact are required.", "error")
            return render_template("employees/form.html", employee=None)
        emp = Employee(name=name, role=role, contact=contact)
        db.session.add(emp)
        db.session.commit()
        flash("Employee added.", "success")
        return redirect(url_for("employees.list_employees"))
    return render_template("employees/form.html", employee=None)


@bp.route("/<int:emp_id>/edit", methods=["GET", "POST"])
@login_required
def edit(emp_id):
    emp = db.session.get(Employee, emp_id)
    if emp is None:
        flash("Employee not found.", "error")
        return redirect(url_for("employees.list_employees"))
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        role = (request.form.get("role") or "").strip()
        contact = (request.form.get("contact") or "").strip()
        if not name or not role or not contact:
            flash("Name, role, and contact are required.", "error")
            return render_template("employees/form.html", employee=emp)
        emp.name = name
        emp.role = role
        emp.contact = contact
        db.session.commit()
        flash("Employee updated.", "success")
        return redirect(url_for("employees.list_employees"))
    return render_template("employees/form.html", employee=emp)


@bp.route("/<int:emp_id>/delete", methods=["POST"])
@login_required
def delete(emp_id):
    emp = db.session.get(Employee, emp_id)
    if emp is None:
        flash("Employee not found.", "error")
    else:
        db.session.delete(emp)
        db.session.commit()
        flash("Employee deleted.", "success")
    return redirect(url_for("employees.list_employees"))
