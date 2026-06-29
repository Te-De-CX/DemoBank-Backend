from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'beneficiaries', views.BeneficiaryViewSet, basename='beneficiary')

urlpatterns = [
    path('', include(router.urls)),
    path('wallet/', views.WalletView.as_view(), name='wallet'),
]