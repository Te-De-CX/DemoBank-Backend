from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from users.models import User
from transactions.models import Transaction
from accounts.models import Account
from accounts.serializers import AccountSerializer      # <-- ADD THIS LINE
from .serializers import AdminUserSerializer, AdminTransactionSerializer, DashboardSummarySerializer
from .permissions import IsAdminUser

class AdminDashboardView(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        data = {
            'total_users': User.objects.count(),
            'total_transactions': Transaction.objects.count(),
            'total_volume': Transaction.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0,
        }
        return Response(DashboardSummarySerializer(data).data)

class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['email', 'first_name', 'last_name']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'is_active': user.is_active})

    @action(detail=True, methods=['post'])
    def approve_kyc(self, request, pk=None):
        user = self.get_object()
        user.kyc_status = 'verified'
        user.save()
        return Response({'kyc_status': user.kyc_status})

class AdminTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = AdminTransactionSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['status', 'transaction_type']
    search_fields = ['reference', 'account__account_number']

class AdminAccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer  # reuse accounts serializer
    permission_classes = [IsAdminUser]