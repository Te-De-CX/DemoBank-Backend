from django.db import models
from common.models import TimeStampedModel
from accounts.models import Account

class Transaction(TimeStampedModel):
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
        ('loan_disbursement', 'Loan Disbursement'),
        ('loan_repayment', 'Loan Repayment'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    recipient_account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.PROTECT, related_name='incoming_transactions')
    recipient_name = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.reference} - {self.amount}"

class BillPayment(models.Model):
    BILL_TYPES = [
        ('airtime', 'Airtime'),
        ('internet', 'Internet'),
        ('utilities', 'Utilities'),
        ('cable', 'Cable TV'),
        ('education', 'Education'),
    ]
    user = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='bill_payments')
    bill_type = models.CharField(max_length=20, choices=BILL_TYPES)
    provider = models.CharField(max_length=100)
    customer_reference = models.CharField(max_length=100)  # phone number, account ID
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction = models.OneToOneField(Transaction, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bill_type} - {self.amount}"