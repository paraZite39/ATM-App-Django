from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime

'''class User(models.Model):
    user_name = models.CharField(max_length = 200)
    user_surname = models.CharField(max_length = 200)
    user_birthdate = models.DateField()

    def __str__(self):
        # human-friendly string representation of user
        return "{0} {1}, born in {2}".format(self.user_name,
                                             self.user_surname,
                                             self.user_birthdate)

    def has_legal_age(self):
        # check if user respects legal age (18 years) to open a bank account)
        return self.user_birthdate >= datetime.now() - datetime.timedelta(days=6570)
'''
class Balance(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    balance_currency = models.CharField(max_length = 3)
    balance_amount = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0)

    def __str__(self):
        # human-friendly string representation of balance
        return "{0}'s {1} account balance is {2}".format(self.user.username,
                                                             self.balance_currency,
                                                             self.balance_amount)
