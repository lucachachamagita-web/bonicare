from django.urls import path
from . import views

urlpatterns = [
    path('', views.visit_list, name='visit_list'),
    path('new/', views.visit_create, name='visit_create'),
    path('<int:visit_id>/service/', views.service_log_create, name='service_log_create'),
    path('<int:visit_id>/prescribe/', views.prescription_create, name='prescription_create'),
    path('<int:visit_id>/bill/', views.visit_bill, name='visit_bill'),
    path('services/catalog/', views.service_catalog_list, name='service_catalog_list'),
    path('services/catalog/new/', views.service_catalog_create, name='service_catalog_create'),
]
