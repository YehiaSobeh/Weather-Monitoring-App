import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
# from freezegun import freeze_time
from unittest.mock import Mock

# 1) First mock dependencies before any imports
@pytest.fixture(autouse=True)
def mock_pwd_context(monkeypatch):
    mock_ctx = Mock()
    mock_ctx.hash = lambda pw: f"hashed_{pw}"
    mock_ctx.verify = lambda plain, hashed: hashed == f"hashed_{plain}"
    monkeypatch.setattr("app.services.user.pwd_context", mock_ctx)

# 2) Configure fresh metadata for each test
@pytest.fixture(scope="function")
def db_session(monkeypatch):
    # Create new metadata instance
    test_metadata = MetaData()
    
    # Patch the original Base metadata
    from app.models import Base
    monkeypatch.setattr(Base, 'metadata', test_metadata)
    
    # Re-import user model after metadata replacement
    from importlib import reload
    from app import models
    reload(models.user)
    
    # Create fresh in-memory engine
    engine = create_engine("sqlite:///:memory:")
    test_metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    test_metadata.drop_all(engine)

# 3) Import service functions after metadata setup
from app.services.user import (
    hash_password,
    compare_password_with_hash,
    create_user
)
from app.schemas.user import UserCreate
from app.core.security import decode_access_token, decode_refresh_token

# 4) Tests
def test_password_hashing_and_verification():
    plain = "securepassword123"
    hashed = hash_password(plain)
    assert compare_password_with_hash(plain, hashed)
    assert not compare_password_with_hash("wrong", hashed)

