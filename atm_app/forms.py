from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

currency_choices = (("USD", "USD"),
                    ("RON", "RON"),
                    ("EUR", "EUR"),
                    ("GBP", "GBP"))

class AmountForm(forms.Form):
	amount = forms.IntegerField(label="Amount", widget=forms.TextInput(attrs={'style' : 'width: 300px;', 'class': 'form-control'}))
	currency = forms.ChoiceField(label="Currency", widget=forms.Select, choices=currency_choices)

class NewUserForm(UserCreationForm):
        class Meta:
                model = User
                fields = ("username", "email", "password1", "password2")

class ExchangeForm(forms.Form):
        from_currency = forms.ChoiceField(label="From Currency", choices=currency_choices, widget=forms.Select)
        amount = forms.IntegerField(label="Amount")
        to_currency = forms.ChoiceField(label="To Currency", choices=currency_choices, widget=forms.Select)

class TransferForm(forms.Form):
        recipient_user = forms.CharField(label="Recipient User")
        amount = forms.IntegerField(label="Amount")
        currency = forms.ChoiceField(label="Currency", choices=currency_choices, widget=forms.Select)
