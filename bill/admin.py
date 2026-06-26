from django.contrib import admin
from .models import Bill, Expense

admin.site.register(Bill)
admin.site.register(Expense)
