from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from .models import Account, Beneficiary, Wallet
from .serializers import AccountSerializer, BeneficiarySerializer, WalletSerializer
from common.permissions import IsAccountOwner

class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

class BeneficiaryViewSet(viewsets.ModelViewSet):
    serializer_class = BeneficiarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Beneficiary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        return wallet