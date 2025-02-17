import structlog
from celery import shared_task
from django.db import transaction
from django.conf import settings
from .models import EventOutbox
from core.event_log_client import EventLogClient

logger = structlog.get_logger(__name__)
BATCH_SIZE = 100


@shared_task
def send_events_to_clickhouse():
    with transaction.atomic():
        events = list(
            EventOutbox.objects.select_for_update(skip_locked=True).order_by('id')[:BATCH_SIZE]
        )
        if not events:
            logger.info("No events to process")
            return

    logger.info("Processing events", count=len(events))
    try:
        with EventLogClient.init() as client:
            client.insert(events)
    except Exception as e:
        logger.error("Failed to send events to ClickHouse", error=str(e))
        raise

    with transaction.atomic():
        EventOutbox.objects.filter(id__in=[event.id for event in events]).delete()
    logger.info("Successfully processed events", count=len(events))
