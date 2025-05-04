# import asyncio
# import pytest
# from fastapi import HTTPException
# from unittest.mock import MagicMock, patch
# import builtins

# # Import the tasks to test
# from celery_tasks import tasks
# from models import Subscription, Weather, Alert


# MY_EMAIL = "mo.shahin@innopolis.university"
# MY_CITY  = "Innopolis"

# # # Test send_subscription_email
# # def test_send_subscription_email(monkeypatch):
# #     sent = {}
    
# #     def fake_send_mail(email, subject, body):
# #         sent['email'] = email
# #         sent['subject'] = subject
# #         sent['body'] = body
    
# #     monkeypatch.setattr(tasks, 'send_mail', fake_send_mail)
# #     result = tasks.send_subscription_email(MY_EMAIL, MY_CITY)
    
# #     assert sent['email'] == MY_EMAIL
# #     assert sent['subject'] == "Welcome to our Weather Alert System!"  # welcome subject

# # Test send_weather_alert_email

# # def test_send_weather_alert_email(monkeypatch):
# #     sent = {}
# #     payload = {'temperature': 30, 'threshold': 25}

# #     def fake_send_mail(email, subject, body):
# #         sent['email'] = email
# #         sent['subject'] = subject
# #         sent['body'] = body

# #     monkeypatch.setattr(tasks, 'send_mail', fake_send_mail)
# #     result = tasks.send_weather_alert_email(MY_EMAIL, MY_CITY, payload)

# #     assert sent['email'] == MY_EMAIL
# #     assert f'⚠ Weather Alert for {MY_CITY}!' == sent['subject']
# #     assert '30°C' in sent['body']
# #     assert '25°C' in sent['body']
# #     assert 'Stay safe' in sent['body']
# #     assert result == f'Alert email sent to {MY_EMAIL} for {MY_CITY}'

# # Test update_all_weather_data

# # def test_update_all_weather_data(monkeypatch):
# #     # Prepare fake DB session and data
# #     fake_cities = [('Berlin',), ('Paris',), ('Tokyo',), (MY_CITY,)]

# #     class DummyCM:
# #         def __enter__(self_inner):
# #             db = MagicMock()
# #             # query(Subscription.city).all() -> fake_cities
# #             sub_query = MagicMock()
# #             sub_query.all.return_value = fake_cities
# #             db.query.return_value = sub_query
# #             return db

# #         def __exit__(self_inner, exc_type, exc, tb):
# #             return False

# #     monkeypatch.setattr(tasks, 'session_local', lambda: DummyCM())

#     # Patch the async update_weather_data.delay
#     # calls = []
#     # monkeypatch.setattr(tasks.update_weather_data, 'delay', lambda city: calls.append(city))

#     # result = tasks.update_all_weather_data()

#     # assert result == f"Triggered updates for {len(fake_cities)} cities."
#     # assert calls == ['Berlin', 'Paris', 'Tokyo', MY_CITY]

# # Helper classes for check_and_trigger_alerts tests

# # class QueryStub:
# #     def __init__(self, result_list):
# #         self._results = result_list

# #     def all(self):
# #         return self._results

# #     def filter(self, *args, **kwargs):
# #         return self

# #     def first(self):
# #         return self._results[0] if self._results else None

# # # Test check_and_trigger_alerts: missing weather data

# # def test_check_and_trigger_alerts_no_weather():
# #     # Subscription stub
# #     sub = Subscription(id=1, user_id=1, city=MY_CITY, temperature_threshold=20)

# #     def fake_query(model):
# #         if model is Subscription:
# #             return QueryStub([sub])
# #         if model is Weather:
# #             return QueryStub([])
# #         return QueryStub([])

# #     db = MagicMock()
# #     db.query.side_effect = fake_query

# #     with pytest.raises(HTTPException) as exc_info:
# #         tasks.check_and_trigger_alerts(db)
# #     assert exc_info.value.status_code == 404
# #     assert f'No weather data found for city: {MY_CITY}' in str(exc_info.value.detail)

# # Test check_and_trigger_alerts: trigger new alert


# # def test_check_and_trigger_alerts_trigger_alert(monkeypatch):
# #     # Subscription stub
# #     sub = Subscription(id=1, user_id=42, city=MY_CITY, temperature_threshold=15)
# #     # Weather stub above threshold
# #     weather = Weather(city=MY_CITY, temperature=18)
# #     # No existing alert
# #     def fake_query(model):
# #         if model is Subscription:
# #             return QueryStub([sub])
# #         if model is Weather:
# #             return QueryStub([weather])
# #         if model is Alert:
# #             return QueryStub([])
# #         return QueryStub([])

# #     db = MagicMock()
# #     db.query.side_effect = fake_query

# #     # Patch get_email_by_user_id
# #     monkeypatch.setattr(tasks, 'get_email_by_user_id', lambda db_session, user_id: MY_EMAIL)
# #     # Spy on send_weather_alert_email.delay
# #     sent = {}
# #     def fake_delay(email, city, payload):
# #         sent['email'] = email
# #         sent['city'] = city
# #         sent['payload'] = payload
# #     monkeypatch.setattr(tasks.send_weather_alert_email, 'delay', fake_delay)

# #     # Call the function
# #     tasks.check_and_trigger_alerts(db)

# #     # Assertions for DB operations
# #     assert db.add.called
# #     added_alert = db.add.call_args[0][0]
# #     assert isinstance(added_alert, Alert)
# #     assert added_alert.subscription_id == 1
# #     assert added_alert.actual_temperature == 18
# #     assert added_alert.threshold == 15
# #     assert added_alert.is_active is True

# #     assert db.commit.called
# #     assert db.refresh.called

# #     # Assertions for email
# #     assert sent['email'] == MY_EMAIL
# #     assert sent['city'] == MY_CITY
# #     assert sent['payload'] == {'temperature': 18, 'threshold': 15}

# # Test check_and_trigger_alerts: existing active alert -> no new email


# def test_check_and_trigger_alerts_existing_alert(monkeypatch):
#     sub = Subscription(id=2, user_id=7, city=MY_CITY, temperature_threshold=25)
#     weather = Weather(city=MY_CITY, temperature=30)
#     existing_alert = Alert(subscription_id=2, actual_temperature=28, threshold=25, is_active=True)

#     def fake_query(model):
#         if model is Subscription:
#             return QueryStub([sub])
#         if model is Weather:
#             return QueryStub([weather])
#         if model is Alert:
#             return QueryStub([existing_alert])
#         return QueryStub([])

#     db = MagicMock()
#     db.query.side_effect = fake_query

#     # Spy on email
#     monkeypatch.setattr(tasks.send_weather_alert_email, 'delay', lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Should not send")))

#     # Should not raise
#     tasks.check_and_trigger_alerts(db)
#     # No add/commit for new alert
#     assert not db.add.called
#     assert not db.commit.called


# # Test update_weather_data
# def test_update_weather_data(monkeypatch):
#     city = 'Berlin'
#     fake_response = {'temp': 10}
#     async def fake_send_request(url, params):
#         return fake_response
#     monkeypatch.setattr(tasks, 'send_request', fake_send_request)
#     from types import SimpleNamespace
#     monkeypatch.setattr(tasks, 'weather_settings', SimpleNamespace(weather_url='http://api', weather_api_key='7ce72e73f043dc9820932bad0228c598'))
#     class DummyCM:
#         def __enter__(self):
#             self.db = MagicMock()
#             return self.db
#         def __exit__(self, exc_type, exc, tb):
#             return False
#     monkeypatch.setattr(tasks, 'session_local', lambda: DummyCM())
#     called = {}
#     monkeypatch.setattr(tasks, 'store_weather_data', lambda db, data, c: called.setdefault('store', (db, data, c)))
#     monkeypatch.setattr(tasks, 'check_and_trigger_alerts', lambda db: called.setdefault('check', db))
#     printed = []
#     monkeypatch.setattr(builtins, 'print', lambda msg: printed.append(msg))
#     tasks.update_weather_data(city)
#     assert called['store'][1] == fake_response
#     assert called['store'][2] == city
#     assert called['check'] == called['store'][0]
#     assert printed == [f"Updated weather data for {city}"]