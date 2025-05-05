from unittest.mock import create_autospec
from sqlalchemy.orm import Session

from models import Subscription
from crud.subscribe import is_subscribed


def test_is_subscribed_true():
    mock_db = create_autospec(Session)
    mock_db.query().filter().first.return_value = Subscription(user_id=1)
    assert is_subscribed(mock_db, 1) is True


def test_is_subscribed_false():
    mock_db = create_autospec(Session)
    mock_db.query().filter().first.return_value = None
    assert is_subscribed(mock_db, 1) is False
