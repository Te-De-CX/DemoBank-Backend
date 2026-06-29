from rest_framework import serializers
from .models import SavingsGoal, SavingsDeposit

class SavingsGoalSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = SavingsGoal
        fields = '__all__'
        read_only_fields = ('user', 'current_amount', 'is_completed')

    def get_progress(self, obj):
        return obj.progress_percentage()

class SavingsDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsDeposit
        fields = '__all__'
        read_only_fields = ('transaction',)