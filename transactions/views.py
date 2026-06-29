from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction as db_transaction
from .models import Transaction, BillPayment
from .serializers import TransferSerializer, TransactionSerializer, BillPaymentSerializer, TransactionFilterSerializer
from accounts.models import Account
from common.permissions import IsAccountOwner
from common.exceptions import InsufficientFunds
from .tasks import process_transfer_notification

class TransactionViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Transaction.objects.all()

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        serializer = TransferSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with db_transaction.atomic():
            source_account = Account.objects.select_for_update().get(id=data['source_account_id'], user=request.user)
            dest_account = Account.objects.select_for_update().get(account_number=data['recipient_account'])

            if source_account.balance < data['amount']:
                raise InsufficientFunds()

            # Apply limits (simplified)
            source_account.balance -= data['amount']
            dest_account.balance += data['amount']
            source_account.save()
            dest_account.save()

            txn = Transaction.objects.create(
                user=request.user,
                account=source_account,
                transaction_type='transfer',
                amount=data['amount'],
                status='completed',
                recipient_account=dest_account,
                reference=f"TRX{uuid.uuid4().hex[:10].upper()}",
                description=data.get('description', ''),
            )
            # Celery task to send notifications
            process_transfer_notification.delay(txn.id)

        return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bill_payment(self, request):
        serializer = BillPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Deduct from default account (simplified: first checking account)
        account = Account.objects.filter(user=request.user, account_type='checking').first()
        if not account:
            return Response({'error': 'No checking account found.'}, status=400)
        if account.balance < data['amount']:
            raise InsufficientFunds()

        with db_transaction.atomic():
            account.balance -= data['amount']
            account.save()
            txn = Transaction.objects.create(
                user=request.user,
                account=account,
                transaction_type='payment',
                amount=data['amount'],
                status='completed',
                reference=f"BILL{uuid.uuid4().hex[:10].upper()}",
                description=f"{data['bill_type']} payment to {data['provider']}",
            )
            bill = serializer.save(user=request.user, transaction=txn, status='completed')

        return Response({'detail': 'Bill payment successful.', 'transaction': TransactionSerializer(txn).data})

    @action(detail=False, methods=['get'])
    def history(self, request):
        filter_serializer = TransactionFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        queryset = Transaction.objects.filter(user=request.user).order_by('-created_at')
        if filters.get('start_date'):
            queryset = queryset.filter(created_at__date__gte=filters['start_date'])
        if filters.get('end_date'):
            queryset = queryset.filter(created_at__date__lte=filters['end_date'])
        if filters.get('type'):
            queryset = queryset.filter(transaction_type=filters['type'])
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        if filters.get('min_amount'):
            queryset = queryset.filter(amount__gte=filters['min_amount'])
        if filters.get('max_amount'):
            queryset = queryset.filter(amount__lte=filters['max_amount'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(TransactionSerializer(page, many=True).data)
        return Response(TransactionSerializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        # Export as CSV (simplified)
        import csv, io
        queryset = Transaction.objects.filter(user=request.user).order_by('-created_at')
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Date', 'Type', 'Amount', 'Status', 'Reference'])
        for txn in queryset:
            writer.writerow([txn.created_at, txn.transaction_type, txn.amount, txn.status, txn.reference])
        return Response({'csv': buffer.getvalue()})