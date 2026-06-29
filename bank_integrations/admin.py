from django.contrib import admin
from .models import BankProvider, LinkedBankAccount

@admin.register(BankProvider)
class BankProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)

@admin.register(LinkedBankAccount)
class LinkedBankAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'account_number', 'balance', 'last_synced')
    search_fields = ('user__email', 'account_number')