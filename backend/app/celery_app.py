from celery import Celery
from celery.schedules import crontab

from core.config import weather_settings

# the deafult celery queue is 'celery'

# Initialize Celery
app = Celery(
    "weather_tasks",
    broker=f"redis://{weather_settings.redis_host}:{weather_settings.redis_port}/2",
    backend=f"redis://{weather_settings.redis_host}:{weather_settings.redis_port}/2 ",  # results of tasks
)

# automatically discovers and registers tasks from the app.celery_tasks.
app.autodiscover_tasks(["app.celery_tasks.tasks"])


app.conf.beat_schedule = {
    "update-all-weather-data-every-15-min": {
        "task": "update_all_weather_data",
        "schedule": crontab(minute="*/1"),
    },
}
