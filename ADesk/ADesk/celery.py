import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ADesk.settings')

app = Celery('ADesk')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Europe/Moscow'
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'action_every_monday_8am': {
        'task': 'ADesk.tasks.send_mail_monday_8am',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}
