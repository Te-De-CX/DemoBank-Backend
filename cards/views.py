from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VirtualCard
from .serializers import CardSerializer
from common.utils import generate_card_number
from django.utils import timezone
import random

class CardViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = VirtualCard.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def list(self, request):
        cards = self.get_queryset()
        return Response(CardSerializer(cards, many=True).data)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        # Limit number of active cards (e.g., max 3)
        if self.get_queryset().filter(status='active').count() >= 3:
            return Response({'error': 'Maximum active cards limit reached.'}, status=status.HTTP_400_BAD_REQUEST)

        card_number = generate_card_number()
        card = VirtualCard.objects.create(
            user=request.user,
            card_number=card_number,
            cvv=f"{random.randint(100, 999)}",
            expiry_month=timezone.now().month,
            expiry_year=timezone.now().year + 3,
            cardholder_name=request.user.get_full_name(),
        )
        return Response(CardSerializer(card).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        card = self.get_object()
        if card.status != 'active':
            return Response({'error': 'Card is not active.'}, status=400)
        card.status = 'frozen'
        card.save()
        return Response({'status': card.status})

    @action(detail=True, methods=['post'])
    def unfreeze(self, request, pk=None):
        card = self.get_object()
        if card.status != 'frozen':
            return Response({'error': 'Card is not frozen.'}, status=400)
        card.status = 'active'
        card.save()
        return Response({'status': card.status})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        card = self.get_object()
        card.status = 'cancelled'
        card.save()
        return Response({'status': card.status})

    @action(detail=True, methods=['post'])
    def set_spending_limit(self, request, pk=None):
        card = self.get_object()
        limit = request.data.get('limit')
        if not limit or float(limit) <= 0:
            return Response({'error': 'Invalid limit.'}, status=400)
        card.spending_limit = limit
        card.save()
        return Response(CardSerializer(card).data)