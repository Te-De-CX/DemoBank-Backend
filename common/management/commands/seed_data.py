from django.core.management.base import BaseCommand
from users.models import User
from accounts.models import Account, Wallet, Beneficiary
from transactions.models import Transaction
from cards.models import VirtualCard
from loans.models import LoanProduct
from bank_integrations.models import BankProvider
from faker import Faker
import random, uuid
from django.utils import timezone
from datetime import timedelta

fake = Faker()

class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **options):
        # Admin
        if not User.objects.filter(email='admin@bank.com').exists():
            User.objects.create_superuser(
                email='admin@bank.com', password='Admin123!',
                first_name='Admin', last_name='User'
            )

        # Test user
        user, created = User.objects.get_or_create(
            email='user@test.com',
            defaults={
                'first_name': 'John', 'last_name': 'Doe',
                'is_active': True, 'is_verified': True,
            }
        )
        user.set_password('Test123!')
        user.save()

        # Accounts
        acc1, _ = Account.objects.get_or_create(
            user=user, account_type='checking',
            defaults={'account_number': '1000000001', 'balance': 5000.00}
        )
        acc2, _ = Account.objects.get_or_create(
            user=user, account_type='savings',
            defaults={'account_number': '1000000002', 'balance': 12000.00}
        )
        Wallet.objects.get_or_create(user=user, defaults={'balance': 200.00})

        # Beneficiary
        Beneficiary.objects.get_or_create(
            user=user, name='Jane Smith', account_number='2000000001',
            bank_name='MockBank'
        )

        # Transactions
        for _ in range(30):
            Transaction.objects.create(
                user=user,
                account=acc1 if random.choice([True, False]) else acc2,
                transaction_type=random.choice(['deposit', 'withdrawal', 'transfer']),
                amount=random.uniform(10, 500),
                status='completed',
                reference=fake.unique.bothify(text='TRX########'),
                description=fake.sentence(),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )

        # Virtual card
        VirtualCard.objects.get_or_create(
            user=user,
            defaults={
                'card_number': '4111111111111111',
                'cvv': '123',
                'expiry_month': timezone.now().month,
                'expiry_year': timezone.now().year + 3,
                'cardholder_name': 'John Doe',
                'last_four': '1111',
            }
        )

        # Loan products
        LoanProduct.objects.get_or_create(
            name='Personal Loan',
            defaults={'interest_rate': 12.5, 'min_amount': 500, 'max_amount': 100000,
                      'min_duration_months': 6, 'max_duration_months': 60}
        )
        LoanProduct.objects.get_or_create(
            name='Education Loan',
            defaults={'interest_rate': 8.0, 'min_amount': 1000, 'max_amount': 50000,
                      'min_duration_months': 12, 'max_duration_months': 48}
        )

        # Bank providers for integration
        providers = [
            ('Mock Bank', 'mock_bank', 'https://logo.clearbit.com/mock.com'),
            ('Test Bank', 'test_bank', 'https://logo.clearbit.com/test.com'),
        ]
        for name, code, logo in providers:
            BankProvider.objects.get_or_create(name=name, code=code, defaults={'logo_url': logo})

        self.stdout.write(self.style.SUCCESS('Seed data loaded successfully'))