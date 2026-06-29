# common/exceptions.py
from rest_framework.exceptions import APIException

class InsufficientFunds(APIException):
    status_code = 400
    default_detail = 'Insufficient funds in the account.'
    default_code = 'insufficient_funds'