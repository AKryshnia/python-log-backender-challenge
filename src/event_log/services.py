import structlog
from django.db import transaction
from django.conf import settings
from .models import EventOutbox

logger = structlog.get_logger(__name__)


class EventService:
    @staticmethod
    @transaction.atomic
    def log_event(event_type: str, event_context: dict, environment: str = settings.ENVIRONMENT) -> None:
        try:
            event = EventOutbox.objects.create(
                event_type=event_type,
                event_context=event_context,
                environment=environment,
            )
            logger.info("Event logged", event_type=event_type, event_id=event.id)
        except Exception as e:
            logger.error("Failed to log event", error=str(e))
            raise
