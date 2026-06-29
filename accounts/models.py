from django.db import models
from common.models import TimeStampedModel
from users.models import User

class Account(TimeStampedModel):
    ACCOUNT_TYPES = [
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('loan', 'Loan'),
    ]
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='accounts')
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    daily_transfer_limit = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    monthly_transfer_limit = models.DecimalField(max_digits=15, decimal_places=2, default=50000.00)

    def __str__(self):
        return f"{self.account_type} - {self.account_number}"

class Beneficiary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='beneficiaries')
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_code = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('user', 'account_number')

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='wallet')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet of {self.user.email}"