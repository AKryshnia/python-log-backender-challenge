import pytest
from django.conf import settings
from event_log.services import EventService
from event_log.models import EventOutbox


@pytest.mark.django_db
def test_log_event():
    event_type = "test_event"
    event_context = {"key": "value"}
    environment = settings.ENVIRONMENT if hasattr(settings, "ENVIRONMENT") else "Local"

    EventService.log_event(event_type=event_type, event_context=event_context, environment=environment)

    event = EventOutbox.objects.filter(event_type=event_type).first()
    assert event is not None, "The event was not logged"
    assert event.event_context == event_context, "The content of the event does not match the expected value"
