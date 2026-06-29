from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LoginDevice, EmailVerificationToken, PasswordResetToken

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_verified', 'kyc_status', 'date_joined')
    list_filter = ('is_active', 'is_verified', 'kyc_status', 'is_staff', 'is_2fa_enabled')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Security', {'fields': ('is_2fa_enabled', 'totp_secret')}),
        ('KYC', {'fields': ('kyc_status', 'kyc_documents')}),
        ('Preferences', {'fields': ('preferred_language', 'theme')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

admin.site.register(User, UserAdmin)
admin.site.register(LoginDevice)
admin.site.register(EmailVerificationToken)
admin.site.register(PasswordResetToken)