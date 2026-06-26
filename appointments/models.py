from django.db import models
from django.contrib.auth.models import User
from profiles.models import Patient

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('SCHEDULED', 'Scheduled'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')])
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Appt for {self.patient} with {self.doctor} at {self.date_time}"
