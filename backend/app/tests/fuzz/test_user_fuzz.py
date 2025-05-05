import uuid

from fastapi.testclient import TestClient
from hypothesis import given, settings, strategies as st, Verbosity

from app.main import app
from api.deps import get_db
try:
    from api.deps import rate_limit
except ImportError:
    rate_limit = None

from core.db import Base, engine
try:
    from core.db import SessionLocal
except ImportError:
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

settings.register_profile(
    "ci_fast",
    max_examples=50,
    deadline=None,
    verbosity=Verbosity.normal,
)
settings.load_profile("ci_fast")

Base.metadata.create_all(bind=engine)


def _override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
if rate_limit:
    app.dependency_overrides[rate_limit] = lambda: True

client = TestClient(app)
API = "/api/v1"

email_st = st.emails()
password_st = st.text(
    min_size=6,
    max_size=32,
    alphabet=st.characters(blacklist_categories=["Cs", "Cc"]),
)


@given(email=email_st, password=password_st)
def test_register_and_login_roundtrip(email: str, password: str) -> None:
    """If we register successfully, login must work with same creds."""
    reg = client.post(
        f"{API}/user/register",
        json={
            "name": "Fuzz",
            "surname": "Tester",
            "email": email,
            "password": password,
        },
    )
    login = client.post(
        f"{API}/user/login",
        json={"email": email, "password": password},
    )

    if reg.status_code in (200, 201):
        assert login.status_code == 200
    elif reg.status_code == 400:
        assert login.status_code in (200, 401)
    else:
        assert login.status_code in (401, 422)


@given(email=email_st, password=password_st)
def test_login_unregistered_user_fuzz(email: str, password: str) -> None:
    """
    Any email we generate here is prefixed with a fresh UUID, guaranteeing it
    was never registered earlier in this test run.
    """
    local, at, domain = email.partition("@")
    unique_email = f"{uuid.uuid4().hex}_{local}{at}{domain}".lower()

    login = client.post(
        f"{API}/user/login",
        json={"email": unique_email, "password": password},
    )
    assert login.status_code in (401, 422)
