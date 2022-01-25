from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect

from .models import Balance, Transaction
from django.contrib.auth.models import User
from .forms import AmountForm, NewUserForm, ExchangeForm, TransferForm

import decimal
import datetime

def index(request):
    if request.user.is_authenticated:
        template = loader.get_template('atm_app/index.html')
        try:
            latest_transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')[:15]
        except Transaction.DoesNotExist:
            latest_transactions = None
            
        context = {'latest_transactions_list' : latest_transactions}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/accounts/login')
    
def query(request):
    if request.user.is_authenticated:
        try:
            # get list of balances for user
            balance_list = Balance.objects.filter(user=request.user)
        except Balance.DoesNotExist:
            # no balances
            balance_list = None
        
        template = loader.get_template('atm_app/query.html')
        
        context = {
            'username': request.user.username,
            'balance_list': balance_list,
        }
        
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/accounts/login")

def deposit(request):
    if request.user.is_authenticated:
        template = loader.get_template('atm_app/deposit.html')
        if request.method == 'POST':
            form = AmountForm(request.POST)
            if form.is_valid():
                dep_amount = form.cleaned_data['amount']
                dep_currency = form.cleaned_data['currency']

                try:
                    user_balance = Balance.objects.get(user=request.user, balance_currency=dep_currency)
                except Balance.DoesNotExist:
                    # create new account in receiving balance if it doesn't exist
                    new_balance = Balance(user=request.user, balance_currency=dep_currency, balance_amount=dep_amount)
                    new_balance.save()

                    # log transaction
                    transaction = Transaction(user=request.user, timestamp=datetime.datetime.now(), transaction_type="Deposit", currency=dep_currency, amount=dep_amount, details="")
                    transaction.save()
                    return HttpResponseRedirect('/atm/')

                # add funds, save
                user_balance.balance_amount += dep_amount
                user_balance.save()

                # log transaction
                transaction = Transaction(user=request.user, timestamp=datetime.datetime.now(), transaction_type="Deposit", currency=dep_currency, amount=dep_amount, details="")
                transaction.save()
                
                return HttpResponseRedirect('/atm/')
        else:
            form = AmountForm()

        context = {
            'form': form,
        }
        
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/accounts/login')

def register(request):
    if not request.user.is_authenticated:
        template = loader.get_template('register/register.html')
        if request.method == 'POST':
            form = NewUserForm(request.POST)
            if form.is_valid():
                newuser_username = form.cleaned_data['username']
                newuser_email = form.cleaned_data['email']
                newuser_pass = form.cleaned_data['password1']
                if(newuser_pass != form.cleaned_data['password2']):
                    return HttpResponseRedirect('/atm/register')

                newuser = User.objects.create_user(newuser_username, newuser_email, newuser_pass)
                newuser.save()

                return HttpResponseRedirect('/accounts/login')

        else:
            form = NewUserForm()

        context = {
            'form': form,
        }
        
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/atm/')

def withdraw(request):
    if request.user.is_authenticated:
        template = loader.get_template('atm_app/withdraw.html')
        if request.method == 'POST':
            form = AmountForm(request.POST)
            if form.is_valid():
                withdraw_amount = form.cleaned_data['amount']
                withdraw_currency = form.cleaned_data['currency']

                try:
                    user_balance = Balance.objects.get(user=request.user, balance_currency=withdraw_currency)
                except Balance.DoesNotExist:
                    # user doesn't have account in selected currency
                    return HttpResponseRedirect('/atm/')

                if(withdraw_amount > user_balance.balance_amount):
                    # not enough funds to withdraw
                    return HttpResponseRedirect('/atm/')

                # subtract from account, commit
                user_balance.balance_amount -= withdraw_amount
                user_balance.save()

                # create transaction in log
                transaction = Transaction(user=request.user, timestamp=datetime.datetime.now(), transaction_type="Withdraw", currency=withdraw_currency, amount=withdraw_amount, details="")
                transaction.save()
                
                return HttpResponseRedirect('/atm/')
        else:
            form = AmountForm()

        context = {
            'form': form,
        }
        
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/accounts/login')

def exchange(request):
    # dict for exchanging currencies
    currency_exchange_rates = {
        "USD": {
            "EUR": 0.89,
            "RON": 4.38,
            "GBP": 0.74
        },
        "EUR": {
            "USD": 1.13,
            "RON": 4.94,
            "GBP": 0.84
        },
        "RON": {
            "USD": 0.23,
            "EUR": 0.2,
            "GBP": 0.17
        },
        "GBP": {
            "USD": 1.35,
            "EUR": 1.2,
            "RON": 5.92
        }
    }
    
    if request.user.is_authenticated:
        template = loader.get_template('atm_app/exchange.html')
        if request.method == 'POST':
            form = ExchangeForm(request.POST)
            if form.is_valid():
                from_currency = form.cleaned_data['from_currency']
                exchange_amount = form.cleaned_data['amount']
                to_currency = form.cleaned_data['to_currency']

                if from_currency == to_currency:
                    # can't exchange between similar currencies
                    return HttpResponseRedirect('/atm/')

                try:
                    from_balance = Balance.objects.get(user=request.user, balance_currency=from_currency)
                except Balance.DoesNotExist:
                    # user doesn't have an account in the sending currency
                    return HttpResponseRedirect('/atm/')

                try:
                    to_balance = Balance.objects.get(user=request.user, balance_currency=to_currency)
                except Balance.DoesNotExist:
                    # user doesn't have an account in the receiving currency
                    to_balance = Balance(user=request.user, balance_currency=to_currency, balance_amount=0)

                if(exchange_amount > from_balance.balance_amount):
                    # not enough funds in sending currency
                    return HttpResponseRedirect('/atm/')

                final_amount = decimal.Decimal(currency_exchange_rates[from_currency][to_currency]) * exchange_amount

                # add to receiving balance, subtract from sending balance, save
                from_balance.balance_amount -= exchange_amount
                to_balance.balance_amount += final_amount
                from_balance.save()
                to_balance.save()

                # log transaction
                transaction = Transaction(user=request.user, timestamp=datetime.datetime.now(), transaction_type="Exchange", currency=from_currency, amount=exchange_amount, details="Exchanged to " + to_currency)
                transaction.save()
                
                return HttpResponseRedirect('/atm/')
        else:
            form = ExchangeForm()

        context = {
            'form': form,
        }
        
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/accounts/login')

def transfer(request):
    if request.user.is_authenticated:
        template = loader.get_template('atm_app/transfer.html')
        if request.method == 'POST':
            form = TransferForm(request.POST)
            if form.is_valid():
                transfer_currency = form.cleaned_data['currency']
                transfer_amount = form.cleaned_data['amount']
                to_username = form.cleaned_data['recipient_user']


                if request.user.username == to_username or transfer_amount <= 0:
                    # cannot transfer to sending account or an amount of maximum 0
                    return HttpResponseRedirect('/atm/')

                try:
                    from_balance = Balance.objects.get(user=request.user, balance_currency=transfer_currency)
                except Balance.DoesNotExist:
                    # sending account does not exist
                    return HttpResponseRedirect('/atm/')

                if transfer_amount > from_balance.balance_amount:
                    # not enough money in sending account
                    return HttpResponseRedirect('/atm/')

                try:
                    to_user = User.objects.get(username=to_username)
                except User.DoesNotExist:
                    # recipient user not found
                    return HttpResponseRedirect('/atm/')
                
                try:
                    to_balance = Balance.objects.get(user=to_user, balance_currency=transfer_currency)
                except Balance.DoesNotExist:
                    # recipient user doesn't have an account in the chosen currency
                    to_balance = Balance(user=to_user, balance_currency=transfer_currency, amount=0)

                from_balance.balance_amount -= transfer_amount
                to_balance.balance_amount += transfer_amount
                from_balance.save()
                to_balance.save()

                # log transaction for sender
                transaction_sender = Transaction(user=request.user, timestamp=datetime.datetime.now(), transaction_type="Transfer", currency=transfer_currency, amount=transfer_amount, details="Sent money to " + to_username)
                transaction_sender.save()

                # log transaction for receiver
                transaction_receiver = Transaction(user=to_user, timestamp=datetime.datetime.now(), transaction_type="Transfer", currency=transfer_currency, amount=transfer_amount, details="Received money from " + request.user.username)
                transaction_receiver.save()
                
                return HttpResponseRedirect('/atm/')
        else:
            form = TransferForm()

        context = {
            'form': form,
        }
        
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/accounts/login')
