from rest_framework import serializers
from .models import Transaction, BillPayment
from accounts.models import Account
from common.utils import generate_reference

class TransferSerializer(serializers.Serializer):
    source_account_id = serializers.IntegerField()
    recipient_account = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['amount'] <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return data

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('user', 'reference', 'status', 'fee')

class BillPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillPayment
        fields = '__all__'
        read_only_fields = ('user', 'transaction', 'status')

class TransactionFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    type = serializers.ChoiceField(choices=Transaction.TYPE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=Transaction.STATUS_CHOICES, required=False)
    min_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)