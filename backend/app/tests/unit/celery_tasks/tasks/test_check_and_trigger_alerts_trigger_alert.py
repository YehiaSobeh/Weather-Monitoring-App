"""
Tests that check_and_trigger_alerts creates a new Alert and enqueues an email
when temperature ≥ threshold and no active alert exists.
"""

from unittest.mock import MagicMock
from celery_tasks.tasks import check_and_trigger_alerts
from models import Subscription, Weather, Alert


MY_EMAIL = "mo.shahin@innopolis.university"
MY_CITY = "Innopolis"


def test_check_and_trigger_alerts_trigger_alert(monkeypatch, dummy_query):
    sub = Subscription(id=1, user_id=42, city=MY_CITY,
                       temperature_threshold=15)
    weather = Weather(city=MY_CITY, temperature=18)

    # Stub DB queries: one sub, one weather, no existing alerts
    def fake_query(model):
        if model is Subscription:
            return dummy_query([sub])
        if model is Weather:
            return dummy_query([weather])
        if model is Alert:
            return dummy_query([])
        return dummy_query([])
        return None

    db = MagicMock()
    db.query.side_effect = fake_query

    # Stub getting the user email
    monkeypatch.setattr('celery_tasks.tasks.get_email_by_user_id', lambda db,
                        uid: MY_EMAIL)
    # Capture the delay call
    email_call = {}
    monkeypatch.setattr('celery_tasks.tasks.send_weather_alert_email.delay',
                        lambda email, city,
                        payload: email_call.update(email=email,
                                                   city=city, payload=payload))

    check_and_trigger_alerts(db)

    # Verify DB had an Alert added & committed
    assert weather.temperature >= sub.temperature_threshold
    assert db.add.called
    added: Alert = db.add.call_args[0][0]
    assert added.subscription_id == 1
    assert added.actual_temperature == 18
    # And the notification was enqueued
    assert email_call['email'] == MY_EMAIL
    assert email_call['city'] == MY_CITY
