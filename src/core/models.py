from typing import Any

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.updated_at = timezone.now()
        
        if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
            update_fields = set(kwargs['update_fields'])
            update_fields.add("updated_at")
            kwargs['update_fields'] = update_fields
        
        super().save(*args, **kwargs)
