"""
Tests for send_weather_alert_email task.
Ensures alert emails include the right city, temperature, and threshold.
"""

from celery_tasks import tasks

MY_EMAIL = "mo.shahin@innopolis.university"
MY_CITY = "Innopolis"


def test_send_weather_alert_email(monkeypatch):
    sent = {}
    payload = {"temperature": 30, "threshold": 25}

    def fake_send_mail(email, subject, body):
        sent.update(email=email, subject=subject, body=body)

    monkeypatch.setattr(tasks, 'send_mail', fake_send_mail)

    result = tasks.send_weather_alert_email(MY_EMAIL, MY_CITY, payload)

    assert sent['email'] == MY_EMAIL
    body = (
        f"Dear User,\n\n"
        f"The temperature in {MY_CITY} is now {payload['temperature']}°C, "
        f"which exceeds your threshold of {payload['threshold']}°C.\n\n"
        f"Stay safe!\n\n"
        f"— Weather Alert System"
    )
    assert f"⚠ Weather Alert for {MY_CITY}!" == sent['subject']
    assert body == sent['body']
    assert result == f"Alert email sent to {MY_EMAIL} for {MY_CITY}"
