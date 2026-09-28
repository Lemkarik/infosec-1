import bcrypt

from app.extensions import db
from app.models import Product, User


def test_register_hashes_password_and_returns_token(app, client):
    response = client.post(
        "/auth/register", json={"login": "alice", "password": "correct-horse"}
    )

    assert response.status_code == 201
    assert response.get_json()["token"]
    with app.app_context():
        user = db.session.get(User, "alice")
        assert user.password_hash != "correct-horse"
        assert bcrypt.checkpw(b"correct-horse", user.password_hash.encode("ascii"))


def test_login_accepts_valid_credentials(client):
    client.post(
        "/auth/register", json={"login": "alice", "password": "correct-horse"}
    )
    response = client.post(
        "/auth/login", json={"login": "alice", "password": "correct-horse"}
    )

    assert response.status_code == 200
    assert response.get_json()["token_type"] == "Bearer"


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/auth/login", json={"login": "alice", "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_data_requires_token(client):
    assert client.get("/api/data").status_code == 401
    assert client.get(
        "/api/data", headers={"Authorization": "Bearer broken"}
    ).status_code == 401


def test_data_is_available_with_token(client, token):
    response = client.get(
        "/api/data", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_response_escapes_xss(app, client, token):
    with app.app_context():
        db.session.add(Product(data='<script>alert("xss")</script>'))
        db.session.commit()

    response = client.get(
        "/api/data", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.get_json()[0]["data"] == (
        "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"
    )


def test_sql_injection_string_does_not_bypass_login(client):
    client.post(
        "/auth/register", json={"login": "alice", "password": "correct-horse"}
    )
    response = client.post(
        "/auth/login",
        json={"login": "alice' OR '1'='1", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_password_longer_than_bcrypt_byte_limit_is_rejected(client):
    response = client.post(
        "/auth/register",
        json={"login": "alice", "password": "я" * 40},
    )
    assert response.status_code == 400


def test_expired_token_is_rejected(app, client):
    app.config["JWT_EXPIRATION_SECONDS"] = -1
    response = client.post(
        "/auth/register", json={"login": "alice", "password": "correct-horse"}
    )
    expired_token = response.get_json()["token"]

    response = client.get(
        "/api/data", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
