import pytest

from app import create_app


def test_application_refuses_to_start_without_jwt_secret(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(RuntimeError, match="JWT_SECRET must contain at least 32 bytes"):
        create_app({"TESTING": True, "JWT_SECRET": None})
