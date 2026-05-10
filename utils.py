"""Shared helpers: auth decorators and small utilities."""
from functools import wraps

from flask import flash, redirect, session, url_for

from models import User, db


def login_required(view_func):
    """Require a logged-in user (session user_id)."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped


def current_user():
    """Return User instance or None."""
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)
