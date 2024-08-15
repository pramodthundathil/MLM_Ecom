
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MLM.settings')

app = Celery('MLM')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    'update-user-designations-every-day': {
        'task': 'Home.tasks.update_user_designations',
        'schedule': crontab(hour=0, minute=0),  # Executes every day at midnight
    },
}
