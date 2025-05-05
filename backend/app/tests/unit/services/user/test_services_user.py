import pytest
from app.services.user import hash_password, create_user
from app.services.user import compare_password_with_hash

# —— DummySession to capture calls without loading SQLAlchemy Base ——


class DummySession:
    def __init__(self):
        self.added = []
        self.committed = False
        self.refreshed = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        obj.id = 1
        self.refreshed.append(obj)


@pytest.fixture(autouse=True)
def stub_generate_tokens(monkeypatch):
    monkeypatch.setattr(
        "app.services.user.generate_tokens",
        lambda user_id: {"token": user_id}
    )


def test_hash_and_verify_password():
    raw = "mysecret"
    hashed = hash_password(raw)
    assert hashed != raw
    assert compare_password_with_hash(raw, hashed)
    assert not compare_password_with_hash("wrong", hashed)


def test_create_user_persists_and_returns_token():
    db = DummySession()

    class UD:
        name = "Alice"
        email = "alice@example.com"
        password = "pw123"
        surname = "Liddell"

    result = create_user(db, UD)
    assert result == {"token": "1"}

    assert db.committed is True
    assert len(db.added) == 1
    user_obj = db.added[0]
    assert user_obj.name == "Alice"
    assert user_obj.email == "alice@example.com"
    assert user_obj.surname == "Liddell"
    assert user_obj.password != "pw123"
    assert compare_password_with_hash("pw123", user_obj.password)
