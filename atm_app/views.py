from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect

from .models import Balance
from django.contrib.auth.models import User
from .forms import AmountForm, NewUserForm

def index(request):
    template = loader.get_template('atm_app/index.html')
    context = None
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/accounts/login')
    
def query(request):
    if request.user.is_authenticated:
        try:
            balance_list = Balance.objects.filter(user=request.user)
        except Balance.DoesNotExist:
            balance_list = None
        
        template = loader.get_template('atm_app/query.html')
        
        context = {
            'username': request.user.username,
            'balance_list': balance_list,
        }
        
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/accounts/login")

'''def deposit(request):
    template = loader.get_template('atm_app/deposit.html')
    return HttpResponse(template.render(None, request))
'''

def deposit(request):
    if request.user.is_authenticated:
        template = loader.get_template('atm_app/deposit.html')
        if request.method == 'POST':
            form = AmountForm(request.POST)
            if form.is_valid():
                dep_amount = form.cleaned_data['amount']
                dep_currency = form.cleaned_data['currency']

                # MANIPULATING DATABASE, 2PL HERE MAYBE
                try:
                    user_balance = Balance.objects.get(user=request.user, balance_currency=dep_currency)
                except Balance.DoesNotExist:
                    new_balance = Balance(user=request.user, balance_currency=dep_currency, balance_amount=dep_amount)
                    new_balance.save()
                    return HttpResponseRedirect('/atm/')
                
                user_balance.balance_amount += dep_amount
                user_balance.save()
                
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
                    return HttpResponseRedirect('/atm/')

                if(withdraw_amount > user_balance.balance_amount):
                    return HttpResponseRedirect('/atm/')
                
                user_balance.balance_amount -= withdraw_amount
                user_balance.save()
                
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
    return HttpResponseRedirect('/atm/')

def transfer(request):
    return HttpResponseRedirect('/atm/')
