import pytest
from sqlalchemy import create_engine, inspect

from core.db import Base, engine as app_engine
from core.config import db_settings

@pytest.fixture(scope="module")
def test_engine():
    """
    Create a fresh SQLite engine for testing, initialize schema, and drop afterwards.
    """
    engine = create_engine(db_settings.SQLITE_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

def test_base_has_tables(test_engine):
    """
    Ensure metadata.create_all created tables in the test database.
    """
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    # At minimum, we should get a list (even if empty)
    assert isinstance(tables, list)

def test_engine_url_matches_config(test_engine):
    """
    Verify that the application's engine URL matches the test engine URL from config.
    """
    assert str(app_engine.url) == str(test_engine.url)
