import uuid
import random
import string

def generate_reference(prefix='TRX'):
    """Generate a unique transaction reference."""
    return f"{prefix}{uuid.uuid4().hex[:10].upper()}"

def generate_account_number():
    """Generate a random 10-digit account number."""
    return ''.join(random.choices(string.digits, k=10))

def generate_card_number():
    """Generate a valid-looking 16-digit card number (for mock)."""
    return '4' + ''.join(random.choices(string.digits, k=15))