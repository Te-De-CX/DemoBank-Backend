from django.contrib import admin
from .models import LoanProduct, LoanApplication, LoanRepayment

@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate', 'min_amount', 'max_amount', 'is_active')
    list_filter = ('is_active',)

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'amount', 'status', 'monthly_emi', 'created_at')
    list_filter = ('status', 'product')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan', 'amount', 'created_at')