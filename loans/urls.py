from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.LoanProductViewSet)
router.register(r'applications', views.LoanApplicationViewSet, basename='loan-application')

urlpatterns = [
    path('', include(router.urls)),
]