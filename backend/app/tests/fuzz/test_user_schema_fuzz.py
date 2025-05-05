import pytest
from hypothesis import given, strategies as st
from app.schemas.user import UserCreate

hyp = pytest.importorskip("hypothesis", reason="hypothesis not installed")


email_st = st.emails()
name_st = st.text(min_size=1, max_size=50)


@given(name=name_st, email=email_st)
def test_user_create_never_crashes(name, email):
    try:
        UserCreate(name=name, email=email)
    except Exception as exc:

        assert exc.__class__.__name__ in {"ValidationError"}
