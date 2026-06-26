from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.proprietor_dashboard, name='proprietor_dashboard'),
    path('cash-flow/', views.cash_flow_report, name='cash_flow_report'),
    path('orders/', views.orders_report, name='orders_report'),
    path('stock-flow/', views.stock_flow_report, name='stock_flow_report'),
]
