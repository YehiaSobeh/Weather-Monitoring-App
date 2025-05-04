"""
Tests update_weather_data task:
 - that it calls send_request,
 - stores data,
 - triggers alert-check,
 - and prints a confirmation.
"""

import builtins
from types import SimpleNamespace
from unittest.mock import MagicMock
from celery_tasks import tasks

MY_CITY = "Innopolis"


def test_update_weather_data(monkeypatch):
    city = MY_CITY
    fake_data = {"temp": 10}

    # 1) stub the async request
    async def fake_send_request(url, params):
        # Ensure the URL and params are correctly passed
        assert "weather" in url
        assert params["q"] == city
        return fake_data

    monkeypatch.setattr(tasks, "send_request", fake_send_request)

    # 2) stub config settings
    monkeypatch.setattr(tasks, "weather_settings",
                        SimpleNamespace(weather_url="http://api",
                                        weather_api_key="KEY"))

    # 3) dummy DB session context manager
    class CM:
        def __enter__(self):
            # Return a fake DB object
            return MagicMock()

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(tasks, "session_local", lambda: CM())

    # 4) capture calls to store_weather_data and check_and_trigger_alerts
    calls = {}
    monkeypatch.setattr(tasks, "store_weather_data",
                        lambda db, data, city_arg: calls.setdefault("stored", (
                               data, city_arg)))
    monkeypatch.setattr(tasks, "check_and_trigger_alerts",
                        lambda db: calls.setdefault("checked", True))

    # 5) capture print output
    printed = []
    monkeypatch.setattr(builtins, "print", lambda msg: printed.append(msg))

    # Execute the task
    tasks.update_weather_data(city)

    # Assertions for store_weather_data
    assert "stored" in calls, "store_weather_data was not called"
    stored_data, stored_city = calls["stored"]
    assert stored_data == fake_data, "store_weather_data"
    " received unexpected data"
    assert stored_city == city, "store_weather_data received unexpected city"

    # Assertions for check_and_trigger_alerts
    assert calls.get("checked"), "check_and_trigger_alerts was not called"

    # Assertions for print output
    assert printed == [f"Updated weather data for {city}"]
