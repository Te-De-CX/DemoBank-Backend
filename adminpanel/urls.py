from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.AdminUserViewSet)
router.register(r'transactions', views.AdminTransactionViewSet)
router.register(r'accounts', views.AdminAccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/summary/', views.AdminDashboardView.as_view({'get': 'summary'}), name='admin-summary'),
]