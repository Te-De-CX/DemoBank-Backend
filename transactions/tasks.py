from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Transaction

@shared_task
def process_transfer_notification(transaction_id):
    try:
        txn = Transaction.objects.select_related('user', 'account').get(id=transaction_id)
        # Send email to sender
        send_mail(
            'Transfer Successful',
            f'You have successfully transferred {txn.amount} to {txn.recipient_name or txn.recipient_account}. Reference: {txn.reference}',
            settings.DEFAULT_FROM_EMAIL,
            [txn.user.email],
            fail_silently=True,
        )
        # If recipient is internal user, notify them
        if txn.recipient_account and txn.recipient_account.user != txn.user:
            send_mail(
                'Incoming Transfer',
                f'You have received {txn.amount} from {txn.user.get_full_name()}. Reference: {txn.reference}',
                settings.DEFAULT_FROM_EMAIL,
                [txn.recipient_account.user.email],
                fail_silently=True,
            )
    except Transaction.DoesNotExist:
        pass