"""
Fuzz tests for /user/register and /user/login endpoints.

* Works even if core.db has no SessionLocal export.
* Creates the users table once, mocks rate-limiting, etc.
* Uses a fast Hypothesis profile (50 examples per property).
"""

# ---------------------------------------------------------------------#
#   Hypothesis global profile – fast & chatty for CI / local runs      #
# ---------------------------------------------------------------------#
from hypothesis import settings, Verbosity

settings.register_profile(
    "ci_fast",
    max_examples=50,       # default is 200
    deadline=None,         # disable timing checks
    verbosity=Verbosity.normal,
)
settings.load_profile("ci_fast")

# ---------------------------------------------------------------------#
#   Standard library / 3rd-party imports                               #
# ---------------------------------------------------------------------#
import uuid

from fastapi.testclient import TestClient
from hypothesis import given, strategies as st

from app.main import app
from api.deps import get_db

# rate_limit may or may not exist in this project
try:
    from api.deps import rate_limit
except ImportError:
    rate_limit = None

# ---------------------------------------------------------------------#
#   Database setup – ensure users table exists                         #
# ---------------------------------------------------------------------#
from core.db import Base, engine

try:
    # Some code-bases export SessionLocal
    from core.db import SessionLocal
except ImportError:
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import the User model so SQLAlchemy registers the table
from models.user import User  # noqa: F401

Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------#
#   Override FastAPI dependencies for tests                            #
# ---------------------------------------------------------------------#
def _override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
if rate_limit:
    app.dependency_overrides[rate_limit] = lambda: True  # disable throttling

client = TestClient(app)
API = "/api/v1"

# ---------------------------------------------------------------------#
#   Hypothesis strategies                                              #
# ---------------------------------------------------------------------#
email_st = st.emails()
password_st = st.text(
    min_size=6,
    max_size=32,
    alphabet=st.characters(blacklist_categories=["Cs", "Cc"]),  # exclude surrogates & control chars
)

# ---------------------------------------------------------------------#
#   Property 1 – register + login round-trip                           #
# ---------------------------------------------------------------------#
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
        f"{API}/user/login", json={"email": email, "password": password}
    )

    if reg.status_code in (200, 201):           # brand-new user
        assert login.status_code == 200
    elif reg.status_code == 400:                # duplicate email
        assert login.status_code in (200, 401)
    else:                                       # validation failure, etc.
        assert login.status_code in (401, 422)

# ---------------------------------------------------------------------#
#   Property 2 – login with definitely-unregistered credentials        #
# ---------------------------------------------------------------------#
@given(email=email_st, password=password_st)
def test_login_unregistered_user_fuzz(email: str, password: str) -> None:
    """
    Any email we generate here is prefixed with a fresh UUID, guaranteeing it
    was never registered earlier in this test run.
    """
    local, at, domain = email.partition("@")
    unique_email = f"{uuid.uuid4().hex}_{local}{at}{domain}".lower()

    login = client.post(
        f"{API}/user/login", json={"email": unique_email, "password": password}
    )
    assert login.status_code in (401, 422)


# ------------------------------   run it alone with "poetry run pytest -q tests/fuzz/test_user_fuzz.py"        -----------------------------------#