from rest_framework import serializers
from .models import LoanProduct, LoanApplication, LoanRepayment

class LoanProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanProduct
        fields = '__all__'

class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = '__all__'
        read_only_fields = ('user', 'status', 'interest_rate', 'monthly_emi', 'total_payable', 'approved_by', 'disbursed_account')

class LoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepayment
        fields = '__all__'
        read_only_fields = ('transaction',)