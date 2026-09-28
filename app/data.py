from flask import Blueprint, jsonify

from app.extensions import db
from app.models import Product
from app.security import jwt_required, sanitize

data_bp = Blueprint("data", __name__, url_prefix="/api")


@data_bp.get("/data")
@jwt_required
def get_data():
    products = db.session.execute(db.select(Product).order_by(Product.id)).scalars()
    return jsonify([{"id": item.id, "data": sanitize(item.data)} for item in products])
