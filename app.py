"""
Inventory Management System — Flask application entry point.

Run with: flask --app app run --debug
Or: python app.py
"""
import os

from flask import Flask

from config import Config
from models import User, db
from routes.auth import bp as auth_bp
from routes.categories import bp as categories_bp
from routes.employees import bp as employees_bp
from routes.main import bp as main_bp
from routes.products import bp as products_bp
from routes.sales import bp as sales_bp
from routes.suppliers import bp as suppliers_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(sales_bp)

    with app.app_context():
        db.create_all()
        _seed_default_user(app)

    return app


def _seed_default_user(app):
    """Create a demo admin account if no users exist (development convenience)."""
    if User.query.first() is not None:
        return
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "admin123")
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    app.logger.warning(
        "No users found: created default user %r (change password in production).",
        username,
    )


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
