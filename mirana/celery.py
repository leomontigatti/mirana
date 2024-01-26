import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mirana.settings")

app = Celery("mirana")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    # Executes every day at 00:00.
    "update_hiring_status": {
        "name": "Update hiring status",
        "task": "main.tasks.update_hiring_status",
        "schedule": crontab(hour=0, minute=0),
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
