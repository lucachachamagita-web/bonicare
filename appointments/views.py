from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Appointment
from profiles.models import Patient
from django.contrib.auth.models import User
from profiles.permissions import role_required

@login_required
@role_required(['PROPRIETOR', 'DOCTOR', 'ATTENDANT'])
def appointment_list(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'DOCTOR':
        appointments = Appointment.objects.filter(doctor=request.user).order_by('-date_time')
    else:
        appointments = Appointment.objects.all().order_by('-date_time')
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})

@login_required
@role_required(['PROPRIETOR', 'DOCTOR', 'ATTENDANT'])
def appointment_create(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor_id')
        date_time = request.POST.get('date_time')
        notes = request.POST.get('notes')
        
        if not patient_id or not doctor_id:
            patients = Patient.objects.all()
            doctors = User.objects.filter(userprofile__role='DOCTOR')
            return render(request, 'appointments/appointment_form.html', {
                'patients': patients, 
                'doctors': doctors,
                'error': 'Please select both a Patient and a Doctor.'
            })
            
        patient = Patient.objects.get(id=patient_id)
        doctor = User.objects.get(id=doctor_id)
        
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_time=date_time,
            notes=notes,
            status='SCHEDULED'
        )
        return redirect('appointment_list')
        
    patients = Patient.objects.all()
    doctors = User.objects.filter(userprofile__role='DOCTOR')
    return render(request, 'appointments/appointment_form.html', {'patients': patients, 'doctors': doctors})
