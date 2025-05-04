"""
Tests that no new Alert or email is sent if an active alert already exists.
"""

from unittest.mock import MagicMock
from celery_tasks.tasks import check_and_trigger_alerts
from models import Subscription, Weather, Alert

MY_EMAIL = "mo.shahin@innopolis.university"
MY_CITY = "Innopolis"


def test_check_and_trigger_alerts_existing_alert(monkeypatch, dummy_query):
    sub = Subscription(id=2, user_id=7, city=MY_CITY, temperature_threshold=25)
    weather = Weather(city=MY_CITY, temperature=30)
    existing = Alert(subscription_id=2, actual_temperature=28, threshold=25,
                     is_active=True)

    # Stub DB: one sub, one weather, one active alert
    def fake_query(model):
        if model is Subscription:
            return dummy_query([sub])
        if model is Weather:
            return dummy_query([weather])
        if model is Alert:
            return dummy_query([existing])
        return dummy_query([])

    db = MagicMock()
    db.query.side_effect = fake_query

    # If send is called, we blow up
    monkeypatch.setattr('celery_tasks.tasks.send_weather_alert_email.delay',
                        lambda *args, **kwargs:
                        (_ for _ in ()).throw(Exception("Should not send")))

    # Should run silently without raising
    check_and_trigger_alerts(db)
    assert not db.add.called
    assert not db.commit.called
