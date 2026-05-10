"""SQLAlchemy models for the Inventory Management System."""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Application user for session-based login."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    contact = db.Column(db.String(120), nullable=False)


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship("Product", back_populates="category", lazy=True)


class Product(db.Model):
    """Product belongs to one Category and one Supplier (many-to-one each way)."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Numeric(12, 2), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)

    category = db.relationship("Category", back_populates="products")
    supplier = db.relationship("Supplier", backref=db.backref("products", lazy=True))

    line_items = db.relationship("SaleLineItem", back_populates="product", lazy=True)


class Sale(db.Model):
    """A bill / invoice; links to many products via SaleLineItem (many-to-many with payload)."""

    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    # Assigned after insert (INV-000001) so we can use the primary key.
    invoice_number = db.Column(db.String(32), unique=True, nullable=True, index=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    line_items = db.relationship(
        "SaleLineItem", back_populates="sale", cascade="all, delete-orphan"
    )


class SaleLineItem(db.Model):
    """Association table between Sale and Product with quantity and prices at sale time."""

    __tablename__ = "sale_line_items"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)

    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    sale = db.relationship("Sale", back_populates="line_items")
    product = db.relationship("Product", back_populates="line_items")
