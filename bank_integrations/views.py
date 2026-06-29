from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BankProvider, LinkedBankAccount
from .serializers import BankProviderSerializer, LinkedBankAccountSerializer
from .tasks import sync_linked_account
import uuid, random
from django.utils import timezone

class BankListView(generics.ListAPIView):
    queryset = BankProvider.objects.filter(is_active=True)
    serializer_class = BankProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

class LinkBankView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        code = request.data.get('bank_code')
        try:
            provider = BankProvider.objects.get(code=code, is_active=True)
        except BankProvider.DoesNotExist:
            return Response({'error': 'Bank not found.'}, status=404)
        # Mock OAuth redirect
        return Response({'redirect_url': f'https://mock-bank.com/oauth?client_id=digitalbank&state={uuid.uuid4().hex}'})

class LinkBankCallbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        # Simulate callback; in real world, exchange code for token
        provider = BankProvider.objects.first()  # mock: just take first
        if not provider:
            return Response({'error': 'No providers'}, status=400)
        # Create linked account with random data
        account = LinkedBankAccount.objects.create(
            user=request.user,
            provider=provider,
            account_number=str(random.randint(1000000000, 9999999999)),
            account_type='checking',
            balance=random.uniform(100, 10000),
            access_token=uuid.uuid4().hex,
            last_synced=timezone.now()
        )
        return Response(LinkedBankAccountSerializer(account).data)

class LinkedAccountsView(generics.ListAPIView):
    serializer_class = LinkedBankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LinkedBankAccount.objects.filter(user=self.request.user)

class RefreshLinkedAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        try:
            linked = LinkedBankAccount.objects.get(pk=pk, user=request.user)
        except LinkedBankAccount.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        sync_linked_account.delay(linked.id)
        return Response({'detail': 'Sync started.'})