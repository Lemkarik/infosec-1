from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    login = db.Column(db.String(50), primary_key=True)
    password_hash = db.Column(db.String(60), nullable=False)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.String(500), nullable=False)
