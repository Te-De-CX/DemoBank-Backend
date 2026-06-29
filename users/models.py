from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)  # must verify email
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    totp_secret = models.CharField(max_length=64, blank=True, null=True)  # for 2FA

    # Profile
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    kyc_status = models.CharField(max_length=20, default='pending')  # pending, verified, rejected
    kyc_documents = models.JSONField(default=dict, blank=True)
    preferred_language = models.CharField(max_length=5, default='en')
    theme = models.CharField(max_length=10, default='system')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class LoginDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    last_login = models.DateTimeField(auto_now=True)
    is_trusted = models.BooleanField(default=False)
    user_agent = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'device_name', 'ip_address')

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)