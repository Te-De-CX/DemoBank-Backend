from django.db import models
from common.models import TimeStampedModel
from users.models import User

class SavingsGoal(TimeStampedModel):
    GOAL_TYPES = [
        ('fixed', 'Fixed'),
        ('flexible', 'Flexible'),
        ('round_up', 'Round-Up'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deadline = models.DateField(null=True, blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default='flexible')
    is_completed = models.BooleanField(default=False)
    auto_round_up = models.BooleanField(default=False)  # for round-up savings
    linked_account = models.ForeignKey('accounts.Account', null=True, on_delete=models.SET_NULL, related_name='savings_goals')

    def progress_percentage(self):
        if self.target_amount > 0:
            return min(100, round((self.current_amount / self.target_amount) * 100, 2))
        return 0

class SavingsDeposit(TimeStampedModel):
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name='deposits')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction = models.ForeignKey('transactions.Transaction', null=True, on_delete=models.SET_NULL)
    note = models.CharField(max_length=200, blank=True)