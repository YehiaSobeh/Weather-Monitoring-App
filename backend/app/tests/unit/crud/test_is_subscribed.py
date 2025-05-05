import pytest
from unittest.mock import MagicMock, create_autospec, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from schemas import SubscriptionRequest
from models import Subscription
from services.subscribe import user_subscribe
from crud.subscribe import is_subscribed


def test_is_subscribed_true():
    mock_db = create_autospec(Session)
    mock_db.query().filter().first.return_value = Subscription(user_id=1)
    assert is_subscribed(mock_db, 1) is True

def test_is_subscribed_false():
    mock_db = create_autospec(Session)
    mock_db.query().filter().first.return_value = None
    assert is_subscribed(mock_db, 1) is False