from django.urls import path
from . import views

urlpatterns = [
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.patient_create, name='patient_create'),
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/new/', views.staff_create, name='staff_create'),
    path('staff/<int:staff_id>/edit/', views.staff_edit, name='staff_edit'),
    path('staff/<int:staff_id>/delete/', views.staff_delete, name='staff_delete'),
    path('salaries/', views.salary_list, name='salary_list'),
    path('salaries/new/', views.salary_create, name='salary_create'),
    path('salaries/generate/', views.generate_payroll, name='generate_payroll'),
    path('salaries/<int:salary_id>/edit/', views.salary_edit, name='salary_edit'),
    path('salaries/<int:salary_id>/delete/', views.salary_delete, name='salary_delete'),
]
