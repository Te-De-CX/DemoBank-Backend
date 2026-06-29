from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend_verification'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('login-2fa/', views.Login2FAView.as_view(), name='login_2fa'),
    path('enable-2fa/', views.Enable2FAView.as_view(), name='enable_2fa'),
    path('disable-2fa/', views.Disable2FAView.as_view(), name='disable_2fa'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('devices/', views.DeviceListView.as_view(), name='devices'),
    path('devices/<int:device_id>/trust/', views.TrustDeviceView.as_view(), name='trust_device'),
]