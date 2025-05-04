"""
Tests that check_and_trigger_alerts raises a 404 if no weather data exists.
"""

import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from celery_tasks.tasks import check_and_trigger_alerts
from models import Subscription, Weather

MY_CITY = "Innopolis"


def test_check_and_trigger_alerts_no_weather(monkeypatch, dummy_query):
    # One subscription, but no Weather rows
    sub = Subscription(id=1, user_id=1, city=MY_CITY, temperature_threshold=20)

    def fake_query(model):
        if model is Subscription:
            return dummy_query([sub])
        if model is Weather:
            return dummy_query([])
        return dummy_query([])

    db = MagicMock()
    db.query.side_effect = fake_query

    with pytest.raises(HTTPException) as exc_info:
        check_and_trigger_alerts(db)

    assert exc_info.value.status_code == 404
    assert f"No weather data found for city: {MY_CITY}" in str(
        exc_info.value.detail)
