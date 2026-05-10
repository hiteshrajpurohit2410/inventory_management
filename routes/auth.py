"""Login and logout routes."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import User, db
from utils import current_user

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "error")
            return render_template("auth/login.html")

        session.clear()
        session["user_id"] = user.id
        flash("You are logged in.", "success")
        next_url = request.args.get("next")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
