from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from profiles.models import Patient
from appointments.models import Appointment

class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, null=True, blank=True, on_delete=models.SET_NULL)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    vitals_bp = models.CharField(max_length=20, blank=True)
    vitals_temp = models.CharField(max_length=10, blank=True)
    clinical_notes = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    is_closed = models.BooleanField(default=False)

    def clean(self):
        if self.is_closed:
            if hasattr(self, 'bill') and self.bill.is_paid == False:
                raise ValidationError("Cannot close visit: Outstanding balance remains.")

class ServiceCatalog(models.Model):
    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ServiceRecord(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(ServiceCatalog, on_delete=models.PROTECT)
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    applied_price = models.DecimalField(max_digits=10, decimal_places=2)

class Prescription(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='prescriptions')
    item = models.ForeignKey('stock.StockItem', on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    prescribed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_dispensed = models.BooleanField(default=False)
