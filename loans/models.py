from django.db import models
from common.models import TimeStampedModel
from users.models import User
from accounts.models import Account

class LoanProduct(models.Model):
    name = models.CharField(max_length=100)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # annual percentage
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    min_duration_months = models.IntegerField()
    max_duration_months = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.interest_rate}%)"

class LoanApplication(TimeStampedModel):
    STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('closed', 'Closed'),
    ]
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='loans')
    product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration_months = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # snapshot
    monthly_emi = models.DecimalField(max_digits=12, decimal_places=2)
    total_payable = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    disbursed_account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='loan_disbursements')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_loans')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Loan {self.id} - {self.amount}"

class LoanRepayment(TimeStampedModel):
    loan = models.ForeignKey(LoanApplication, on_delete=models.PROTECT, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction = models.ForeignKey('transactions.Transaction', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Repayment for Loan {self.loan.id}"