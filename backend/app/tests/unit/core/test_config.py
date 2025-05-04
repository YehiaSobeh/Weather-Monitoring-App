import os
import pytest
from core.config import db_settings

def test_default_sqlite_url():
    # by default in your .env or config you expect an SQLite URL
    assert db_settings.SQLITE_DATABASE_URL.startswith("sqlite:///")

def test_override_via_env(monkeypatch):
    monkeypatch.setenv("SQLITE_DATABASE_URL", "sqlite:///./test.db")
    from importlib import reload
    import core.config as cfg
    reload(cfg)
    assert cfg.db_settings.SQLITE_DATABASE_URL == "sqlite:///./test.db"
