from rest_framework import serializers
from .models import VirtualCard

class CardSerializer(serializers.ModelSerializer):
    card_number_masked = serializers.SerializerMethodField()

    class Meta:
        model = VirtualCard
        fields = ['id', 'card_number_masked', 'cvv', 'expiry_month', 'expiry_year', 'cardholder_name',
                  'status', 'spending_limit', 'daily_spent', 'last_four', 'created_at']
        read_only_fields = ('card_number', 'cvv', 'daily_spent', 'created_at')

    def get_card_number_masked(self, obj):
        return f"**** **** **** {obj.last_four}"