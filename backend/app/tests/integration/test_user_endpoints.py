import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient
import json
from main import app

# 1) Import your FastAPI app and the exact module your router lives in:
from app.main import app
import api.endpoints.user as user_endpoints

client = TestClient(app)


@pytest.fixture(autouse=True)
def disable_db(monkeypatch):
    # Replace get_db so we never open a real database session
    monkeypatch.setattr(
        user_endpoints,
        "get_db",
        lambda: iter([None])  # yields one None
    )
    yield


def test_register_success(monkeypatch):
    fake_tokens = {"access_token": "MOCK_A", "refresh_token": "MOCK_R"}

    # Stub out the checks inside register()
    monkeypatch.setattr(
        user_endpoints.crud_user,
        "check_if_user_with_email_exists",
        lambda db, email: False
    )
    monkeypatch.setattr(
        user_endpoints.users_service,
        "create_user",
        lambda db, data: fake_tokens
    )

    resp = client.post(
        "/api/v1/user/register",
        json={"name": "X", "surname": "Y", "email": "x@y.com", "password": "pw"}
    )
    assert resp.status_code == 200
    assert resp.json() == fake_tokens


def test_register_duplicate(monkeypatch):
    # Force the duplicate branch
    monkeypatch.setattr(
        user_endpoints.crud_user,
        "check_if_user_with_email_exists",
        lambda db, email: True
    )

    resp = client.post(
        "/api/v1/user/register",
        json={"name": "A", "surname": "B", "email": "a@b.com", "password": "pw"}
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Email already in use"}


def test_login_success(monkeypatch):
    fake_user = SimpleNamespace(id="42", password="hashedpw")
    # Must include all fields your response model expects:
    fake_tokens = {
        "access_token": "ACC42",
        "refresh_token": "REF42",
        "expires_in":  123,
        "refresh_token_expires_in": 456
    }

    monkeypatch.setattr(
        user_endpoints.crud_user,
        "get_user_by_email",
        lambda db, email: fake_user
    )
    monkeypatch.setattr(
        user_endpoints.users_service,
        "compare_password_with_hash",
        lambda inp, stored: True
    )
    monkeypatch.setattr(
        user_endpoints,
        "generate_tokens",
        lambda uid: fake_tokens
    )

    resp = client.post(
        "/api/v1/user/login",
        json={"email": "any@one.com", "password": "whatever"}
    )
    assert resp.status_code == 200
    assert resp.json() == fake_tokens


@pytest.mark.parametrize("user_obj,password_ok", [
    (None, False),
    (SimpleNamespace(id="1", password="hash"), False),
])
def test_login_failures(monkeypatch, user_obj, password_ok):
    # no user or wrong password → 401
    monkeypatch.setattr(
        user_endpoints.crud_user,
        "get_user_by_email",
        lambda db, email: user_obj
    )
    monkeypatch.setattr(
        user_endpoints.users_service,
        "compare_password_with_hash",
        lambda inp, stored: password_ok
    )

    resp = client.post(
        "/api/v1/user/login",
        json={"email": "x@y.com", "password": "nopass"}
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid credentials."}


@pytest.mark.parametrize("payload, missing_field", [
    
    ({"surname": "Y","email": "x@y.com","password":"pw"}, "name"),
    ({"name": "X",     "email": "x@y.com","password":"pw"}, "surname"),
    ({"name": "X",     "surname":"Y",      "password":"pw"}, "email"),
    ({"name": "X",     "surname":"Y",      "email": "x@y.com"}, "password"),
])
def test_register_validation_error(payload, missing_field):
    resp = client.post("/api/v1/user/register", json=payload)
    assert resp.status_code == 422




