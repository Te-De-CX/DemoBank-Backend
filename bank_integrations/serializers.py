from rest_framework import serializers
from .models import BankProvider, LinkedBankAccount

class BankProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankProvider
        fields = '__all__'

class LinkedBankAccountSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)

    class Meta:
        model = LinkedBankAccount
        fields = '__all__'
        read_only_fields = ('user', 'access_token', 'last_synced')