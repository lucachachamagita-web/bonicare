from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('new/', views.stock_item_create, name='stock_item_create'),
    path('movement/', views.stock_movement, name='stock_movement'),
    path('otc/', views.otc_sale_create, name='otc_sale_create'),
    path('approvals/', views.stock_approvals, name='stock_approvals'),
]
