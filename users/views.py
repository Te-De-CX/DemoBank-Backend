from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from datetime import timedelta
import pyotp, uuid

from .serializers import *
from .models import EmailVerificationToken, PasswordResetToken, LoginDevice
from .tasks import send_email_verification, send_password_reset_email, send_2fa_code_email
from .permissions import IsVerified

User = get_user_model()

def set_auth_cookies(response, refresh):
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
    refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()

    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=access_token,
        max_age=int(access_lifetime),
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=True,
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        value=refresh_token,
        max_age=int(refresh_lifetime),
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=True,
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )
    return response

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Send verification email asynchronously
        send_email_verification(user.id)
        return Response({'detail': 'Registration successful. Please check your email to verify your account.'},
                        status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        token = request.data.get('token')
        try:
            verification = EmailVerificationToken.objects.get(token=token, is_used=False)
            if verification.is_expired():
                return Response({'error': 'Verification link expired.'}, status=status.HTTP_400_BAD_REQUEST)
            user = verification.user
            user.is_active = True
            user.is_verified = True
            user.save()
            verification.is_used = True
            verification.save()
            return Response({'detail': 'Email verified successfully.'})
        except EmailVerificationToken.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            return Response({'detail': 'If this email is registered, a new verification link has been sent.'})
        send_email_verification(user.id)
        return Response({'detail': 'Verification email resent.'})

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(email=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'error': 'Please verify your email first.'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_2fa_enabled:
            # Generate and send 2FA code (via email in this example)
            code = pyotp.TOTP(user.totp_secret).now()
            send_2fa_code_email.delay(user.id, code)
            return Response({'require_2fa': True, 'email': user.email}, status=status.HTTP_200_OK)

        refresh = RefreshToken.for_user(user)
        response = Response({'detail': 'Login successful.'})
        set_auth_cookies(response, refresh)

        # Record device – safely get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        ip = request.META.get('REMOTE_ADDR')
        # Use a simple device name derived from the user agent string (first 50 chars)
        device_name = user_agent[:50] if user_agent else 'Unknown Device'
        LoginDevice.objects.update_or_create(
            user=user,
            device_name=device_name,
            ip_address=ip,
            defaults={'last_login': timezone.now(), 'user_agent': user_agent}
        )
        user.last_login_ip = ip
        user.save(update_fields=['last_login_ip'])
        return response

class Login2FAView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = TwoFALoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if not user or not user.is_2fa_enabled:
            return Response({'error': 'Invalid credentials or 2FA not enabled.'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(serializer.validated_data['totp_code']):
            return Response({'error': 'Invalid 2FA code.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        response = Response({'detail': 'Login successful.'})
        set_auth_cookies(response, refresh)
        return response

class Enable2FAView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVerified]
    def post(self, request):
        user = request.user
        if user.is_2fa_enabled:
            return Response({'error': '2FA is already enabled.'}, status=status.HTTP_400_BAD_REQUEST)

        # For enabling, generate a TOTP secret and return a provisioning URI for QR code
        secret = pyotp.random_base32()
        user.totp_secret = secret
        user.save()
        provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(user.email, issuer_name='DigitalBank')
        return Response({'secret': secret, 'qr_code_uri': provisioning_uri})

    def put(self, request):
        """Confirm enabling after scanning QR."""
        user = request.user
        code = request.data.get('totp_code')
        if not user.totp_secret:
            return Response({'error': 'Initiate 2FA setup first.'}, status=status.HTTP_400_BAD_REQUEST)
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code):
            user.is_2fa_enabled = True
            user.save()
            return Response({'detail': '2FA enabled.'})
        return Response({'error': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

class Disable2FAView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        user = request.user
        user.is_2fa_enabled = False
        user.totp_secret = None
        user.save()
        return Response({'detail': '2FA disabled.'})

class LogoutView(APIView):
    def post(self, request):
        response = Response({'detail': 'Logged out.'})
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'], path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'], path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'])
        # Invalidate refresh token if using blacklist; here we just clear cookies.
        return response

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        # Re-issue tokens to prevent logout? Or force re-login. We'll keep simple.
        return Response({'detail': 'Password changed.'})

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({'detail': 'If that email exists, a reset link has been sent.'})
        token = PasswordResetToken.objects.create(
            user=user,
            token=uuid.uuid4().hex,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        send_password_reset_email.delay(user.id, token.token)
        return Response({'detail': 'Password reset email sent.'})

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        token_str = request.data.get('token')
        new_password = request.data.get('new_password')
        try:
            reset_token = PasswordResetToken.objects.get(token=token_str, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        if reset_token.is_expired():
            return Response({'error': 'Token expired.'}, status=status.HTTP_400_BAD_REQUEST)
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        reset_token.is_used = True
        reset_token.save()
        return Response({'detail': 'Password reset successful.'})

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    def get_object(self):
        return self.request.user

class DeviceListView(generics.ListAPIView):
    serializer_class = DeviceSerializer
    def get_queryset(self):
        return LoginDevice.objects.filter(user=self.request.user).order_by('-last_login')

class TrustDeviceView(APIView):
    def post(self, request, device_id):
        device = LoginDevice.objects.get(id=device_id, user=request.user)
        device.is_trusted = True
        device.save()
        return Response({'status': 'trusted'})