from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SavingsGoal, SavingsDeposit
from .serializers import SavingsGoalSerializer, SavingsDepositSerializer
from accounts.models import Account
from transactions.models import Transaction
from common.utils import generate_reference

class SavingsGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SavingsGoal.objects.none()   # dummy, overridden by get_queryset

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        goal = self.get_object()
        amount = request.data.get('amount')
        from_account_id = request.data.get('account_id')
        if not amount or not from_account_id:
            return Response({'error': 'amount and account_id required'}, status=400)

        try:
            account = Account.objects.get(id=from_account_id, user=request.user)
        except Account.DoesNotExist:
            return Response({'error': 'Invalid account.'}, status=400)

        amount = float(amount)
        if account.balance < amount:
            return Response({'error': 'Insufficient funds.'}, status=400)

        with db_transaction.atomic():
            account.balance -= amount
            account.save()
            txn = Transaction.objects.create(
                user=request.user,
                account=account,
                transaction_type='transfer',
                amount=amount,
                status='completed',
                reference=f"SAV{generate_reference('SV')[:8]}",
                description=f"Deposit to savings goal: {goal.name}"
            )
            deposit = SavingsDeposit.objects.create(goal=goal, amount=amount, transaction=txn)
            goal.current_amount += amount
            if goal.current_amount >= goal.target_amount:
                goal.is_completed = True
            goal.save()

        return Response(SavingsGoalSerializer(goal).data)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        # Withdraw from goal to linked account (simplified)
        goal = self.get_object()
        if not goal.linked_account:
            return Response({'error': 'No linked account for withdrawal.'}, status=400)
        amount = request.data.get('amount')
        amount = float(amount)
        if amount > goal.current_amount:
            return Response({'error': 'Amount exceeds goal balance.'}, status=400)

        with db_transaction.atomic():
            goal.current_amount -= amount
            goal.save()
            goal.linked_account.balance += amount
            goal.linked_account.save()
            # create reversal transaction?
        return Response(SavingsGoalSerializer(goal).data)