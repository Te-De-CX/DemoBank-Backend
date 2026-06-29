from django.contrib import admin
from .models import Account, Beneficiary, Wallet

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'account_type', 'balance', 'currency', 'is_active')
    list_filter = ('account_type', 'currency', 'is_active')
    search_fields = ('account_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number', 'bank_name', 'user')
    search_fields = ('name', 'account_number')

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')