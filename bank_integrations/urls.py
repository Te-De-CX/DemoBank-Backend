from django.urls import path
from . import views

urlpatterns = [
    path('providers/', views.BankListView.as_view(), name='bank-list'),
    path('link/', views.LinkBankView.as_view(), name='link-bank'),
    path('link/callback/', views.LinkBankCallbackView.as_view(), name='link-callback'),
    path('linked-accounts/', views.LinkedAccountsView.as_view(), name='linked-accounts'),
    path('linked-accounts/<int:pk>/refresh/', views.RefreshLinkedAccountView.as_view(), name='refresh-account'),
]