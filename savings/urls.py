from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'goals', views.SavingsGoalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]