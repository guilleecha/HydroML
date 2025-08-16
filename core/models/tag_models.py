# core/models/tag_models.py
import uuid
from django.db import models
from taggit.models import TagBase, GenericUUIDTaggedItemBase

class UUIDTag(TagBase):
    # This is a custom Tag model that you could extend in the future if needed.
    # For now, it just inherits the base functionality.
    pass

class UUIDTaggedItem(GenericUUIDTaggedItemBase, models.Model):
    # This is the core of the solution. It tells taggit to use a UUIDField
    # for the object_id, which links to your model's primary key.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.ForeignKey(
        UUIDTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )

    class Meta:
        verbose_name = "Tagged Item"
        verbose_name_plural = "Tagged Items"
        app_label = "core"  # Or any central app
