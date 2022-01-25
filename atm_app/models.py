from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime
class Balance(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    balance_currency = models.CharField(max_length = 3)
    balance_amount = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0)

    def __str__(self):
        # human-friendly string representation of balance
        return "{0}'s {1} account balance is {2}".format(self.user.username,
                                                             self.balance_currency,
                                                             self.balance_amount)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    timestamp = models.DateTimeField()
    transaction_type = models.CharField(max_length = 10)
    currency = models.CharField(max_length = 3)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    details = models.CharField(max_length = 30)
