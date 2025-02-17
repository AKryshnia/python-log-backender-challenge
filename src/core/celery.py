from celery import Celery
from django.conf import settings

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-events-to-clickhouse': {
        'task': 'event_log.tasks.send_events_to_clickhouse',
        'schedule': 60.0,
    },
}
