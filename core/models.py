from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """
    Model to store user notifications for ML experiments and other events.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who will receive this notification"
    )
    message = models.TextField(
        help_text="The notification message content"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the user has read this notification"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the notification was created"
    )
    link = models.URLField(
        blank=True,
        null=True,
        help_text="Optional URL to link to relevant page (e.g., experiment detail)"
    )
    
    # Optional fields for categorization and context
    notification_type = models.CharField(
        max_length=50,
        default='experiment',
        choices=[
            ('experiment', 'Experiment'),
            ('dataset', 'Dataset'),
            ('system', 'System'),
        ],
        help_text="Type of notification for categorization"
    )
    related_object_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="ID of the related object (e.g., experiment ID)"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."
    
    def mark_as_read(self):
        """Mark this notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
