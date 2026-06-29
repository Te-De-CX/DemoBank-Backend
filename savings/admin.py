from django.contrib import admin
from .models import SavingsGoal, SavingsDeposit

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_amount', 'current_amount', 'goal_type', 'is_completed')
    list_filter = ('goal_type', 'is_completed')
    search_fields = ('user__email', 'name')

@admin.register(SavingsDeposit)
class SavingsDepositAdmin(admin.ModelAdmin):
    list_display = ('id', 'goal', 'amount', 'created_at')