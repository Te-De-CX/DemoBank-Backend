from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/cards/', include('cards.urls')),
    path('api/loans/', include('loans.urls')),
    path('api/savings/', include('savings.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/admin/', include('adminpanel.urls')),
    path('api/bank/', include('bank_integrations.urls')),
    # Swagger documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]