from datetime import datetime, timedelta, timezone
from functools import wraps
from html import escape

import jwt
from flask import current_app, g, jsonify, request


def create_token(login: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": login,
        "iat": now,
        "exp": now
        + timedelta(seconds=current_app.config["JWT_EXPIRATION_SECONDS"]),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def jwt_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, separator, token = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not token:
            return jsonify(error="Missing or invalid Authorization header"), 401

        try:
            claims = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=["HS256"],
                options={"require": ["sub", "iat", "exp"]},
            )
            if not isinstance(claims["sub"], str) or not claims["sub"]:
                raise jwt.InvalidTokenError("Invalid subject")
        except jwt.PyJWTError:
            return jsonify(error="Invalid or expired token"), 401

        g.current_user = claims["sub"]
        return view(*args, **kwargs)

    return wrapped


def sanitize(value: str) -> str:
    """Escape untrusted strings before returning them in an API response."""
    return escape(value, quote=True)
