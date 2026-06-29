from rest_framework import serializers
from users.models import User
from transactions.models import Transaction
from accounts.models import Account

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_verified', 'kyc_status', 'date_joined')

class AdminTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class DashboardSummarySerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_transactions = serializers.IntegerField()
    total_volume = serializers.DecimalField(max_digits=15, decimal_places=2)