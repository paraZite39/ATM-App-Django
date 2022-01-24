from django import forms

currency_choices = [("USD", "USD"),
                    ("RON", "RON"),
                    ("EUR", "EUR"),
                    ("GBP", "GBP")]

class AmountForm(forms.Form):
	amount = forms.IntegerField(label="Amount")
	currency = forms.ChoiceField(label="Currency", choices=currency_choices, widget=forms.RadioSelect)
