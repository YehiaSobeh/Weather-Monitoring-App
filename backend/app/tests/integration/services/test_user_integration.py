from importlib import reload
from unittest.mock import Mock

import pytest
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

import app.models as models
from app.services.user import hash_password, compare_password_with_hash


@pytest.fixture(autouse=True)
def mock_pwd_context(monkeypatch):
    mock_ctx = Mock()
    mock_ctx.hash = lambda pw: f"hashed_{pw}"
    mock_ctx.verify = lambda plain, hashed: hashed == f"hashed_{plain}"
    monkeypatch.setattr("app.services.user.pwd_context", mock_ctx)
    yield


@pytest.fixture(scope="function")
def db_session(monkeypatch):
    test_metadata = MetaData()
    models.Base.metadata = test_metadata
    reload(models.user)
    engine = create_engine("sqlite:///:memory:")
    test_metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    test_metadata.drop_all(engine)


def test_password_hashing_and_verification():
    plain = "securepassword123"
    hashed = hash_password(plain)
    assert compare_password_with_hash(plain, hashed)
    assert not compare_password_with_hash("wrong", hashed)
