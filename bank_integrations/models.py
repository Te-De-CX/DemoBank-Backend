from django.db import models
from common.models import TimeStampedModel
from users.models import User

class BankProvider(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    logo_url = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LinkedBankAccount(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='linked_banks')
    provider = models.ForeignKey(BankProvider, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=30)
    account_type = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    last_synced = models.DateTimeField(null=True)
    access_token = models.CharField(max_length=255)  # mock token

    class Meta:
        unique_together = ('user', 'provider', 'account_number')