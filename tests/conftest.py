import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET": "test-only-secret-that-is-long-enough-123456",
            "JWT_EXPIRATION_SECONDS": 3600,
            "SEED_DATA": False,
        }
    )
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def token(client):
    response = client.post(
        "/auth/register",
        json={"login": "alice", "password": "correct-horse"},
    )
    return response.get_json()["token"]
