from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Patient, UserProfile, SalaryRecord
from profiles.permissions import role_required

@login_required
@role_required(['PROPRIETOR', 'DOCTOR', 'ATTENDANT'])
def patient_list(request):
    patients = Patient.objects.all().order_by('-registered_at')
    return render(request, 'profiles/patient_list.html', {'patients': patients})

@login_required
@role_required(['PROPRIETOR', 'DOCTOR', 'ATTENDANT'])
def patient_create(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        dob = request.POST.get('dob')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        Patient.objects.create(
            patient_id=patient_id,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            phone=phone,
            address=address,
            registered_by=request.user
        )
        return redirect('patient_list')
        
    return render(request, 'profiles/patient_form.html')

@login_required
@role_required(['PROPRIETOR'])
def staff_list(request):
    staff = UserProfile.objects.all().select_related('user')
    return render(request, 'profiles/staff_list.html', {'staff': staff})

@login_required
@role_required(['PROPRIETOR'])
def staff_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        phone = request.POST.get('phone')
        basic_salary = request.POST.get('basic_salary', '0.00')
        
        from django.contrib import messages
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists. Please choose a different one.")
            return render(request, 'profiles/staff_form.html')
            
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        if role == 'PROPRIETOR':
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
        UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone,
            basic_salary=basic_salary
        )
        messages.success(request, f"Staff member '{username}' registered successfully.")
        return redirect('staff_list')
    return render(request, 'profiles/staff_form.html')

@login_required
@role_required(['PROPRIETOR'])
def staff_edit(request, staff_id):
    staff_profile = get_object_or_404(UserProfile, id=staff_id)
    if request.method == 'POST':
        staff_profile.user.first_name = request.POST.get('first_name')
        staff_profile.user.last_name = request.POST.get('last_name')
        staff_profile.user.email = request.POST.get('email')
        staff_profile.user.save()
        
        staff_profile.role = request.POST.get('role')
        staff_profile.phone = request.POST.get('phone')
        staff_profile.basic_salary = request.POST.get('basic_salary', '0.00')
        staff_profile.save()
        
        return redirect('staff_list')
    return render(request, 'profiles/staff_edit.html', {'staff_profile': staff_profile})

@login_required
@role_required(['PROPRIETOR'])
def staff_delete(request, staff_id):
    staff_profile = get_object_or_404(UserProfile, id=staff_id)
    if request.method == 'POST':
        staff_profile.user.delete()  # This will cascade and delete UserProfile
        return redirect('staff_list')
    return render(request, 'profiles/staff_confirm_delete.html', {'staff_profile': staff_profile})

@login_required
@role_required(['PROPRIETOR'])
def salary_list(request):
    salaries = SalaryRecord.objects.all().order_by('-month')
    return render(request, 'profiles/salary_list.html', {'salaries': salaries})

@login_required
@role_required(['PROPRIETOR'])
def salary_create(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        month = request.POST.get('month')
        base_salary = request.POST.get('base_salary')
        bonus = request.POST.get('bonus', '0')
        is_paid = request.POST.get('is_paid') == 'on'
        
        employee = User.objects.get(id=employee_id)
        
        SalaryRecord.objects.create(
            employee=employee,
            month=month + '-01',  # Store as first day of the selected month
            base_salary=base_salary,
            bonus=bonus,
            is_paid=is_paid
        )
        return redirect('salary_list')
        
    staff = UserProfile.objects.all()
    return render(request, 'profiles/salary_form.html', {'staff': staff})

@login_required
@role_required(['PROPRIETOR'])
def generate_payroll(request):
    if request.method == 'POST':
        month_input = request.POST.get('payroll_month')
        if month_input:
            month_date = month_input + '-01'
            staff = UserProfile.objects.all()
            for s in staff:
                SalaryRecord.objects.get_or_create(
                    employee=s.user,
                    month=month_date,
                    defaults={
                        'base_salary': s.basic_salary,
                        'bonus': 0.00,
                        'is_paid': False
                    }
                )
    return redirect('salary_list')

@login_required
@role_required(['PROPRIETOR'])
def salary_edit(request, salary_id):
    salary = get_object_or_404(SalaryRecord, id=salary_id)
    if request.method == 'POST':
        salary.base_salary = request.POST.get('base_salary')
        salary.bonus = request.POST.get('bonus', '0')
        salary.is_paid = request.POST.get('is_paid') == 'on'
        salary.save()
        return redirect('salary_list')
    return render(request, 'profiles/salary_edit.html', {'salary': salary})

@login_required
@role_required(['PROPRIETOR'])
def salary_delete(request, salary_id):
    salary = get_object_or_404(SalaryRecord, id=salary_id)
    if request.method == 'POST':
        salary.delete()
        return redirect('salary_list')
    return render(request, 'profiles/salary_confirm_delete.html', {'salary': salary})
