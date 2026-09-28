import logging

import bcrypt
from flask import Blueprint, jsonify, request, current_app

from app.extensions import db
from app.models import User
from app.security import create_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _credentials_from_request() -> tuple[str, str] | None:
    body = request.get_json(silent=True)
    current_app.logger.warning(f"request: {request.data}")
    current_app.logger.warning(f"body: {body}")
    if not isinstance(body, dict):
        return None

    login = body.get("login")
    password = body.get("password")
    current_app.logger.warning(f"login: {login}\n password: {password}")
    if not isinstance(login, str) or not isinstance(password, str):
        return None
    if not 5 <= len(login) <= 50 or not 8 <= len(password) <= 72:
        return None
    if not login.strip() or not password.strip():
        return None
    if len(password.encode("utf-8")) > 72:
        return None
    return login, password


@auth_bp.post("/register")
def register():
    credentials = _credentials_from_request()
    if credentials is None:
        return jsonify(error="Login must be 5-50 characters and password 8-72"), 400

    login, password = credentials
    if db.session.get(User, login) is not None:
        return jsonify(error="User already exists"), 409

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("ascii")
    db.session.add(User(login=login, password_hash=password_hash))
    db.session.commit()
    return jsonify({"token": create_token(login), "token_type": "Bearer"}), 201


@auth_bp.post("/login")
def login():
    credentials = _credentials_from_request()
    if credentials is None:
        return jsonify(error="Invalid login or password"), 401

    login, password = credentials
    user = db.session.get(User, login)
    if user is None or not bcrypt.checkpw(
        password.encode("utf-8"), user.password_hash.encode("ascii")
    ):
        return jsonify(error="Invalid login or password"), 401

    return jsonify({"token": create_token(user.login), "token_type": "Bearer"}), 200
