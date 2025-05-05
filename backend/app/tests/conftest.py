import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.db import Base
from api.deps import (
    get_cache_redis,
    get_db, rate_limit,
    get_user_id_from_token
)
from main import app
from core.config import db_settings


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        db_settings.SQLITE_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    TestSession = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    connection = db_engine.connect()
    _ = connection.begin()
    session = TestSession(bind=connection)

    yield session

    # this make sure that the database is empty before the next test starts.
    session.rollback()  # Undo all changes
    connection.close()


class DummyQuery:
    """
    A stand-in for SQLAlchemy Query that supports:
     - .all()
     - .filter(...).order_by(...).first()
    """
    def __init__(self, results):
        self._results = results

    def all(self):
        return self._results

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._results[0] if self._results else None


@pytest.fixture
def dummy_query():
    """
    Factory for DummyQuery:
      dummy_query([a, b, c]) -> DummyQuery([a, b, c])
    """
    return DummyQuery


@pytest.fixture
def subscription_data():
    return {
        "email": "saleemasekrea000@gmail.com",
        "city": "New York",
        "condition_thresholds": {
            "temperature": 70,
        },
    }


@pytest.fixture
def client(db_session):
    """
    Bind the TestClient to use our db_session for every request.
    """
    # override get_db to yield the db_session
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    return TestClient(app)


# https://fastapi.tiangolo.com/advanced/testing-dependencies/#use-the-appdependency_overrides-attribute
# Mock dependencies for the tests

"""
autouse : True means that this fixture
will be automatically used by all tests
wthiout the need to explicitly pass it
as an argument to the test function.
 """


@pytest.fixture(autouse=True)
def override_dependencies():
    def mock_get_db():
        return "mock_db"

    def mock_get_cache_redis():
        return "mock_redis"

    def mock_rate_limit():
        return True

    def mock_get_user():
        return 1

    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_cache_redis] = mock_get_cache_redis
    app.dependency_overrides[rate_limit] = mock_rate_limit
    app.dependency_overrides[get_user_id_from_token] = mock_get_user

    yield

    app.dependency_overrides.clear()
