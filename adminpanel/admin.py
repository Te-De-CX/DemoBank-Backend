from django.contrib import admin
from .models import SupportTicket, SystemLog

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('subject', 'user__email')

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'created_at')
    list_filter = ('action',)
    search_fields = ('user__email',)