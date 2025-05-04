"""
Hypothesis property test for the UserCreate schema.

Skipped automatically if Hypothesis isn’t installed.
"""
import pytest

hyp = pytest.importorskip("hypothesis", reason="hypothesis not installed")
from hypothesis import given, strategies as st

from app.schemas.user import UserCreate


email_st = st.emails()
name_st = st.text(min_size=1, max_size=50)


@given(name=name_st, email=email_st)
def test_user_create_never_crashes(name, email):
    """
    Creating UserCreate with arbitrary valid-looking name/email should never
    raise anything other than pydantic ValidationError.
    """
    try:
        UserCreate(name=name, email=email)
    except Exception as exc:
        # Hypothesis will shrink & highlight any *unexpected* exception.
        assert exc.__class__.__name__ in {"ValidationError"}
