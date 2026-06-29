from celery import shared_task
from .models import LinkedBankAccount
from django.utils import timezone
import random

@shared_task
def sync_linked_account(linked_id):
    try:
        linked = LinkedBankAccount.objects.get(id=linked_id)
        # Mock sync: update balance with a random change
        linked.balance += random.uniform(-50, 200)
        linked.last_synced = timezone.now()
        linked.save()
    except LinkedBankAccount.DoesNotExist:
        pass