import asyncio
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.celery_app import app
from core.db import session_local
from mailingsys.mailer import send_mail
from models import Alert, Subscription, Weather
from core.config import weather_settings
from utils.weather import send_request, store_weather_data
from crud.user import get_email_by_user_id
import logging

logger = logging.getLogger(__name__)


@app.task(name="send_subscription_email")
def send_subscription_email(user_email: str, city: str):
    subject = "Welcome to our Weather Alert System!"
    body = (
        f"Thank you for subscribing to Weather Alerts! "
        f"You will now receive weather alerts for {city}."
    )

    send_mail(user_email, subject, body)
    return "Email sent successfully!"


@app.task(name="send_weather_alert_email")
def send_weather_alert_email(user_email: str, city: str, payload: dict):
    """
    Sends an alert email when a subscription’s
    temperature threshold is crossed.
    """
    subject = f"⚠ Weather Alert for {city}!"
    body = (
        f"Dear User,\n\n"
        f"The temperature in {city} is now {payload['temperature']}°C, "
        f"which exceeds your threshold of {payload['threshold']}°C.\n\n"
        f"Stay safe!\n\n"
        f"— Weather Alert System"
    )
    send_mail(user_email, subject, body)
    return f"Alert email sent to {user_email} for {city}"


@app.task(name="update_weather_data")
def update_weather_data(city: str):
    """
    Updates weather data for a given city and
    checks if any alert conditions are triggered.
    """
    url = f"{weather_settings.weather_url}/weather"

    params = {
        "q": city,
        "appid": weather_settings.weather_api_key,
    }
    # here i create a mini loop event to be able to wait for the response
    # as celery task is sync ...
    weather_data = asyncio.run(send_request(url, params))
    with session_local() as db:
        store_weather_data(db, weather_data, city)
        check_and_trigger_alerts(db)
    print(f"Updated weather data for {city}")


@app.task(name="update_all_weather_data")
def update_all_weather_data():
    """
    Updates weather data for all subscribed cities.
    """
    with session_local() as db:
        cities = db.query(Subscription.city).all()
        # cities will be a list of tuples, so extract city names
        city_list = [city[0] for city in cities]
    for city in city_list:
        update_weather_data.delay(city)

    return f"Triggered updates for {len(city_list)} cities."


def check_and_trigger_alerts(db: Session) -> None:
    """
    Check all active subscriptions and compare their thresholds against
    the latest weather data. If a threshold is exceeded, create an alert
    and send a notification email.
    """
    subscriptions = db.query(Subscription).all()

    for sub in subscriptions:
        sub_city = sub.city.lower()
        # Get the latest weather data for the subscriber's city
        weather = (
            db.query(Weather)
            .filter(Weather.city == sub_city)
            .order_by(desc(Weather.fetched_at))
            .first()
        )
        if not weather:
            raise HTTPException(
                status_code=404,
                detail=f"No weather data found for city: {sub.city}"
            )

        # Check if the weather condition exceeds the subscriber's threshold
        if weather.temperature >= sub.temperature_threshold:
            # Check if an active alert already exists for this subscription
            existing_alert = (
                db.query(Alert)
                .filter(
                    Alert.subscription_id == sub.id,
                    Alert.is_active
                )
                .first()
            )

            if not existing_alert:
                user_email = get_email_by_user_id(db, sub.user_id)
                # Create a new alert
                alert = Alert(
                    subscription_id=sub.id,
                    actual_temperature=weather.temperature,
                    threshold=sub.temperature_threshold,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(alert)
                db.commit()
                db.refresh(alert)

                # Send notification asynchronously
                send_weather_alert_email.delay(
                    user_email,
                    sub.city,
                    {
                        "temperature": weather.temperature,
                        "threshold": sub.temperature_threshold,
                    },
                )
