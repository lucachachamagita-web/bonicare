from django.contrib import admin
from .models import UserProfile, Patient, SalaryRecord

admin.site.register(UserProfile)
admin.site.register(Patient)
admin.site.register(SalaryRecord)
