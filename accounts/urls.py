from django.urls import path

from . import views

urlpatterns = [
    path('cashier/', views.Cashier.as_view(), name='cashier'),
    path('transactions/', views.Transactions.as_view(), name='transactions'),
    path('buy/', views.Buy.as_view(), name='buy'),
]