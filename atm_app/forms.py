from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

currency_choices = [("USD", "USD"),
                    ("RON", "RON"),
                    ("EUR", "EUR"),
                    ("GBP", "GBP")]

class AmountForm(forms.Form):
	amount = forms.IntegerField(label="Amount")
	currency = forms.ChoiceField(label="Currency", choices=currency_choices, widget=forms.RadioSelect)

class NewUserForm(UserCreationForm):
        class Meta:
                model = User
                fields = ("username", "email", "password1", "password2")
