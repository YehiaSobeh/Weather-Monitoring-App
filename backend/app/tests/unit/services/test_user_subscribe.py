import pytest
from unittest.mock import MagicMock, create_autospec, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from schemas import SubscriptionRequest
from services.subscribe import user_subscribe


def test_user_subscribe_already_subscribed():
    mock_db = create_autospec(Session)
    subscription_data = SubscriptionRequest(city="TestCity",
                                            temperature_threshold=25.5)
    with patch('services.subscribe.is_subscribed', return_value=True):
        with pytest.raises(HTTPException) as exc:
            user_subscribe(db=mock_db, subscription=subscription_data,
                           user_id=1)

        assert exc.value.status_code == 400
        assert "already has a subscription" in str(exc.value.detail)


def test_user_subscribe_success():
    mock_db = create_autospec(Session)
    subscription_data = SubscriptionRequest(city="kazan",
                                            temperature_threshold=25.5)

    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    mock_db.query().filter().first.return_value = mock_user

    with patch(
        'services.subscribe.is_subscribed',
        return_value=False,
    ), patch(
        'services.subscribe.send_subscription_email.delay',
    ) as mock_send:

        result = user_subscribe(db=mock_db, subscription=subscription_data,
                                user_id=1)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(result)
    mock_send.assert_called_once_with("test@example.com", "kazan")
