"""
Tests for update_all_weather_data task.
Checks that we fetch all subscribed cities and enqueue an update for each.
"""

from unittest.mock import MagicMock
from celery_tasks import tasks


MY_CITY = "Innopolis"


def test_update_all_weather_data(monkeypatch):
    fake_cities = [('Berlin',), ('Paris',), ('Tokyo',), (MY_CITY,)]
    # Dummy context manager returning our fake DB

    class DummyCM:
        def __enter__(self):
            db = MagicMock()
            q = MagicMock()
            q.all.return_value = fake_cities
            db.query.return_value = q
            return db

        def __exit__(self, *args):
            return False

    # Patch out session_local
    monkeypatch.setattr(tasks, 'session_local', lambda: DummyCM())

    # Capture which cities get enqueued
    calls = []
    monkeypatch.setattr(tasks.update_weather_data, 'delay',
                        lambda city: calls.append(city))

    out = tasks.update_all_weather_data()

    assert out == "Triggered updates for 4 cities."
    assert calls == ['Berlin', 'Paris', 'Tokyo', MY_CITY]
