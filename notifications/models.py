from django.db import models
from users.models import User
from common.models import TimeStampedModel

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('transaction', 'Transaction'),
        ('security', 'Security Alert'),
        ('promo', 'Promotional'),
        ('system', 'System'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, blank=True)  # extra payload

    class Meta:
        ordering = ['-created_at']