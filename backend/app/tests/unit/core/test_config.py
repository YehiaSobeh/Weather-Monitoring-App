from core.config import db_settings
from importlib import reload
import core.config as cfg


def test_default_sqlite_url():
    assert db_settings.SQLITE_DATABASE_URL.startswith("sqlite:///")


def test_override_via_env(monkeypatch):
    monkeypatch.setenv("SQLITE_DATABASE_URL", "sqlite:///./test.db")

    reload(cfg)
    assert cfg.db_settings.SQLITE_DATABASE_URL == "sqlite:///./test.db"
