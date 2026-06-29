from django.db import models
from users.models import User
from common.models import TimeStampedModel

class SupportTicket(TimeStampedModel):
    STATUS = [('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='open')

class SystemLog(TimeStampedModel):
    ACTION_CHOICES = [('login', 'Login'), ('transfer', 'Transfer'), ('admin_action', 'Admin Action')]
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict)