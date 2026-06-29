from django.db import models
from common.models import TimeStampedModel
from users.models import User
from common.utils import generate_card_number

class VirtualCard(TimeStampedModel):
    CARD_STATUS = [
        ('active', 'Active'),
        ('frozen', 'Frozen'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cards')
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=4)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    cardholder_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=CARD_STATUS, default='active')
    spending_limit = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    daily_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_four = models.CharField(max_length=4)

    def __str__(self):
        return f"Card ****{self.last_four} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.last_four and self.card_number:
            self.last_four = self.card_number[-4:]
        super().save(*args, **kwargs)