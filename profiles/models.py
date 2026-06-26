from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('PROPRIETOR', 'Proprietor/Admin'),
        ('DOCTOR', 'Doctor'),
        ('ATTENDANT', 'Reception/Lab Attendant')
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Patient(models.Model):
    patient_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    registered_at = models.DateTimeField(auto_now_add=True)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_id})"

class SalaryRecord(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
