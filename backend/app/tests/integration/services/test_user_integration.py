import pytest
from unittest.mock import Mock
from app.services.user import (
    hash_password,
    compare_password_with_hash,
)


@pytest.fixture(autouse=True)
def mock_pwd_context(monkeypatch):
    mock_ctx = Mock()
    mock_ctx.hash = lambda pw: f"hashed_{pw}"
    mock_ctx.verify = lambda plain, hashed: hashed == f"hashed_{plain}"
    monkeypatch.setattr("app.services.user.pwd_context", mock_ctx)


def test_password_hashing_and_verification():
    plain = "securepassword123"
    hashed = hash_password(plain)
    assert compare_password_with_hash(plain, hashed)
    assert not compare_password_with_hash("wrong", hashed)
