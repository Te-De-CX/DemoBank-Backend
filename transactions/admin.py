from django.contrib import admin
from .models import Transaction, BillPayment

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference', 'account__account_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(BillPayment)
class BillPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bill_type', 'provider', 'amount', 'status', 'created_at')
    list_filter = ('bill_type', 'status')
    search_fields = ('user__email', 'provider')