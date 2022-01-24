from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect

from .models import User, Balance
from .forms import AmountForm

def index(request):
    template = loader.get_template('atm_app/index.html')
    context = None
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Please log in.")
    
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
        return HttpResponse("Please log in.")

'''def deposit(request):
    template = loader.get_template('atm_app/deposit.html')
    return HttpResponse(template.render(None, request))
'''

def deposit(request):
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

def withdraw(request):
    template = loader.get_template('atm_app/withdraw.html')
    if request.method == 'POST':
        form = AmountForm(request.POST)
        if form.is_valid():
            withdraw_amount = form.cleaned_data['amount']
            withdraw_currency = form.cleaned_data['currency']

            # MANIPULATING DATABASE, 2PL HERE MAYBE
            try:
                user_balance = Balance.objects.get(user=request.user, balance_currency=withdraw_currency)
            except Balance.DoesNotExist:
                return HttpResponseRedirect('/atm/')

            if(withdraw_amount > user_balance.balance_amount):
                # ERROR - NOT ENOUGH FUNDS
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
