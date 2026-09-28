import os
import secrets

from dotenv import load_dotenv
from flask import Flask, jsonify

from app.extensions import db


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL", "sqlite:///infosec.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET=os.getenv("JWT_SECRET") or secrets.token_urlsafe(32),
        JWT_EXPIRATION_SECONDS=int(os.getenv("JWT_EXPIRATION_SECONDS", "3600")),
        SEED_DATA=True,
    )

    if test_config:
        app.config.update(test_config)

    _validate_security_config(app)

    db.init_app(app)

    from app.auth import auth_bp
    from app.data import data_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(data_bp)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify(error="Resource not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify(error="Internal server error"), 500

    @app.after_request
    def add_security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    with app.app_context():
        db.create_all()
        if app.config["SEED_DATA"]:
            _seed_products()

    return app


def _validate_security_config(app: Flask) -> None:
    secret = app.config["JWT_SECRET"]
    expiration = app.config["JWT_EXPIRATION_SECONDS"]
    if not isinstance(secret, str) or len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 bytes")
    if not isinstance(expiration, int) or expiration <= 0:
        raise RuntimeError("JWT_EXPIRATION_SECONDS must be a positive integer")


def _seed_products() -> None:
    from app.models import Product

    if db.session.execute(db.select(Product.id).limit(1)).scalar() is None:
        db.session.add_all(
            [Product(data="Security handbook"), Product(data="API checklist")]
        )
        db.session.commit()
