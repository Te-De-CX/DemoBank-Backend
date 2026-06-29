from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerificationToken, User
import uuid
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_email_verification(user_id):
    try:
        user = User.objects.get(id=user_id)
        token = EmailVerificationToken.objects.create(
            user=user,
            token=uuid.uuid4().hex,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"
        send_mail(
            'Verify your email address',
            f'Click the link to verify: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        pass

@shared_task
def send_password_reset_email(user_id, token):
    user = User.objects.get(id=user_id)
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    send_mail(
        'Password Reset Request',
        f'Click the link to reset your password: {reset_link}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

@shared_task
def send_2fa_code_email(user_id, code):
    user = User.objects.get(id=user_id)
    send_mail(
        'Your 2FA Code',
        f'Your login verification code is: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )