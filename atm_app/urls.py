from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('query', views.query, name='query'),
    path('deposit', views.deposit, name='deposit'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('register', views.register, name='register'),
    path('exchange', views.exchange, name='exchange'),
    path('transfer', views.transfer, name='transfer')
]
