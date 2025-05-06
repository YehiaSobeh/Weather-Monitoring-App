"""
Tests for send_subscription_email task.
Verifies that the welcome email is constructed and sent correctly.
"""

from celery_tasks import tasks

MY_EMAIL = "mo.shahin@innopolis.university"
MY_CITY = "Innopolis"


def test_send_subscription_email(monkeypatch):
    sent = {}
    # Stub out the actual mailer

    def fake_send_mail(email, subject, body):
        sent['email'], sent['subject'], sent['body'] = email, subject, body

    monkeypatch.setattr(tasks, 'send_mail', fake_send_mail)

    # Call the task
    result = tasks.send_subscription_email(MY_EMAIL, MY_CITY)

    # Verify the mail was “sent” with the right data
    assert sent['email'] == MY_EMAIL
    assert sent['subject'] == "Welcome to our Weather Alert System!"
    body = (
        "Thank you for subscribing to Weather Alerts! "
        f"You will now receive weather alerts for {MY_CITY}."
    )
    assert body == sent['body']
    assert result == "Email sent successfully!"
