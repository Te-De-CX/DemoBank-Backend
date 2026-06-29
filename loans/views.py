from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LoanProduct, LoanApplication
from .serializers import LoanProductSerializer, LoanApplicationSerializer
from .calculators import calculate_emi, calculate_total_payable
from accounts.models import Account
from common.exceptions import InsufficientFunds

class LoanProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoanProduct.objects.filter(is_active=True)
    serializer_class = LoanProductSerializer
    permission_classes = [permissions.AllowAny]  # public to browse products

class LoanApplicationViewSet(viewsets.GenericViewSet):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LoanApplication.objects.filter(user=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        return Response(LoanApplicationSerializer(queryset, many=True).data)

    def create(self, request):
        # Application creation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = request.data.get('product')
        try:
            product = LoanProduct.objects.get(id=product_id, is_active=True)
        except LoanProduct.DoesNotExist:
            return Response({'error': 'Invalid product.'}, status=400)

        amount = serializer.validated_data['amount']
        months = serializer.validated_data['duration_months']
        if amount < product.min_amount or amount > product.max_amount:
            return Response({'error': 'Amount out of range.'}, status=400)
        if months < product.min_duration_months or months > product.max_duration_months:
            return Response({'error': 'Duration out of range.'}, status=400)

        interest = product.interest_rate
        emi = calculate_emi(amount, interest, months)
        total = calculate_total_payable(emi, months)

        loan = serializer.save(
            user=request.user,
            product=product,
            interest_rate=interest,
            monthly_emi=emi,
            total_payable=total,
        )
        return Response(LoanApplicationSerializer(loan).data, status=201)

    @action(detail=True, methods=['post'])
    def repay(self, request, pk=None):
        loan = self.get_object()
        if loan.status not in ['disbursed']:
            return Response({'error': 'Loan cannot be repaid at this time.'}, status=400)
        # Deduct from a source account (simplified: first checking account)
        account = Account.objects.filter(user=request.user, account_type='checking').first()
        if not account or account.balance < loan.monthly_emi:
            raise InsufficientFunds()

        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            account.balance -= loan.monthly_emi
            account.save()
            # Create repayment transaction
            from transactions.models import Transaction
            txn = Transaction.objects.create(
                user=request.user,
                account=account,
                transaction_type='loan_repayment',
                amount=loan.monthly_emi,
                status='completed',
                reference=f"LRP{uuid.uuid4().hex[:10].upper()}",
                description=f"Repayment for loan {loan.id}",
            )
            from .models import LoanRepayment
            LoanRepayment.objects.create(loan=loan, amount=loan.monthly_emi, transaction=txn)

            # Check if loan is fully paid (simplified: count repayments)
            remaining = loan.total_payable - (loan.repayments.aggregate(total=models.Sum('amount'))['total'] or 0) - loan.monthly_emi
            if remaining <= 0:
                loan.status = 'closed'
                loan.save()

        return Response({'detail': 'Repayment successful.'})