from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('<int:bill_id>/pay/', views.bill_pay, name='bill_pay'),
    path('<int:bill_id>/mpesa-pay/', views.bill_mpesa_pay, name='bill_mpesa_pay'),
    path('<int:bill_id>/discharge/', views.bill_discharge, name='bill_discharge'),
    path('<int:bill_id>/receipt/', views.bill_receipt, name='bill_receipt'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/new/', views.expense_create, name='expense_create'),
]
