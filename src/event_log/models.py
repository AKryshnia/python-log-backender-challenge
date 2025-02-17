from django.db import models
from django.utils import timezone


class EventOutbox(models.Model):
    event_type = models.CharField(max_length=255)
    event_date_time = models.DateTimeField(default=timezone.now, db_index=True)
    environment = models.CharField(max_length=255)
    event_context = models.JSONField()
    metadata_version = models.BigIntegerField(default=1)

    class Meta:
        db_table = 'event_outbox'
        ordering = ['id']

    def __str__(self):
        return f"{self.event_type} at {self.event_date_time}"
