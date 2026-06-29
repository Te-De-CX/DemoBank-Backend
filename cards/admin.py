from django.contrib import admin
from .models import VirtualCard

@admin.register(VirtualCard)
class VirtualCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'last_four', 'status', 'spending_limit', 'expiry_month', 'expiry_year')
    list_filter = ('status',)
    search_fields = ('user__email', 'card_number')
    readonly_fields = ('created_at', 'updated_at')