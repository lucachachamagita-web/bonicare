from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Visit, ServiceCatalog, ServiceRecord, Prescription
from stock.models import StockItem
from profiles.models import Patient
from django.contrib.auth.models import User
from profiles.permissions import role_required
from bill.models import Bill

@login_required
@role_required(['PROPRIETOR', 'DOCTOR', 'ATTENDANT'])
def visit_list(request):
    visits = Visit.objects.filter(is_closed=False).order_by('-check_in_time')
    return render(request, 'case/visit_list.html', {'visits': visits})

@login_required
@role_required(['DOCTOR', 'ATTENDANT'])
def visit_create(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor_id')
        
        if not patient_id or not doctor_id:
            patients = Patient.objects.all()
            doctors = User.objects.filter(userprofile__role='DOCTOR')
            return render(request, 'case/visit_form.html', {
                'patients': patients, 
                'doctors': doctors,
                'error': 'Please select both a Patient and a Doctor.'
            })
            
        patient = Patient.objects.get(id=patient_id)
        doctor = User.objects.get(id=doctor_id)
        
        Visit.objects.create(
            patient=patient,
            doctor=doctor
        )
        return redirect('visit_list')
        
    patients = Patient.objects.all()
    doctors = User.objects.filter(userprofile__role='DOCTOR')
    return render(request, 'case/visit_form.html', {'patients': patients, 'doctors': doctors})

@login_required
@role_required(['DOCTOR', 'ATTENDANT'])
def service_log_create(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        quantity = int(request.POST.get('quantity', 1))
        
        service = ServiceCatalog.objects.get(id=service_id)
        
        ServiceRecord.objects.create(
            visit=visit,
            service=service,
            performed_by=request.user,
            quantity=quantity,
            applied_price=service.base_price
        )
        return redirect('visit_list')
        
    services = ServiceCatalog.objects.filter(is_active=True)
    return render(request, 'case/service_form.html', {'visit': visit, 'services': services})

@login_required
@role_required(['DOCTOR'])
def prescription_create(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        item = StockItem.objects.get(id=item_id)
        
        Prescription.objects.create(
            visit=visit,
            item=item,
            prescribed_by=request.user,
            quantity=quantity
        )
        return redirect('visit_list')
        
    items = StockItem.objects.filter(category='MEDICINE', current_quantity__gt=0)
    return render(request, 'case/prescription_form.html', {'visit': visit, 'items': items})

@login_required
@role_required(['DOCTOR', 'ATTENDANT'])
def visit_bill(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    bill = getattr(visit, 'bill', None)
    return render(request, 'case/visit_bill.html', {'visit': visit, 'bill': bill})

@login_required
@role_required(['PROPRIETOR'])
def service_catalog_list(request):
    services = ServiceCatalog.objects.all().order_by('name')
    return render(request, 'case/service_catalog_list.html', {'services': services})

@login_required
@role_required(['PROPRIETOR'])
def service_catalog_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        base_price = request.POST.get('base_price', '0.00')
        
        ServiceCatalog.objects.create(
            name=name,
            base_price=base_price,
            is_active=True
        )
        return redirect('service_catalog_list')
        
    return render(request, 'case/service_catalog_form.html')
