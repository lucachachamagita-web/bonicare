from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Bill, Expense
from case.models import Visit
from stock.models import StockMovement
from profiles.permissions import role_required
from django.core.exceptions import ValidationError
from decimal import Decimal

@login_required
@role_required(['PROPRIETOR', 'DOCTOR', 'ATTENDANT'])
def bill_list(request):
    bills = Bill.objects.all().order_by('-generated_at')
    return render(request, 'bill/bill_list.html', {'bills': bills})

@login_required
@role_required(['DOCTOR', 'ATTENDANT'])
def bill_pay(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    if request.method == 'POST':
        payment_amount = Decimal(request.POST.get('amount_paid', '0.00'))
        discount = Decimal(request.POST.get('discount', '0.00'))
        
        bill.amount_paid += payment_amount
        bill.discount = discount
        
        if bill.amount_paid + bill.discount >= bill.total_amount:
            bill.is_paid = True
            
        bill.generated_by = request.user
        bill.save()
        
        if bill.is_paid:
            bill.visit.is_closed = True
            bill.visit.save()
            
            # Auto-dispense prescriptions
            for rx in bill.visit.prescriptions.filter(is_dispensed=False):
                StockMovement.objects.create(
                    item=rx.item,
                    movement_type='OUT',
                    quantity=rx.quantity,
                    visit=bill.visit,
                    handled_by=request.user,
                    is_approved=True
                )
                rx.item.current_quantity -= rx.quantity
                rx.item.save()
                rx.is_dispensed = True
                rx.save()
                
            return redirect('bill_receipt', bill_id=bill.id)
            
        return redirect('bill_list')
        
    return render(request, 'bill/bill_pay.html', {'bill': bill})

@login_required
@role_required(['PROPRIETOR'])
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'bill/expense_list.html', {'expenses': expenses})

@login_required
@role_required(['PROPRIETOR', 'DOCTOR'])
def expense_create(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        amount = Decimal(request.POST.get('amount', '0.00'))
        date = request.POST.get('date')
        description = request.POST.get('description')
        
        Expense.objects.create(
            category=category,
            amount=amount,
            date=date,
            description=description,
            logged_by=request.user
        )
        
        if request.user.userprofile.role == 'PROPRIETOR':
            return redirect('expense_list')
        else:
            return redirect('home')
            
    return render(request, 'bill/expense_form.html')

@login_required
@role_required(['PROPRIETOR', 'ATTENDANT'])
def bill_receipt(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, 'bill/bill_receipt.html', {'bill': bill})

@login_required
@role_required(['DOCTOR', 'ATTENDANT', 'PROPRIETOR'])
def bill_mpesa_pay(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        amount_str = request.POST.get('amount', '0.00')
        payment_amount = Decimal(amount_str)
        
        # Phone cleaning for Kenyan numbers (format: 2547XXXXXXXX or 2541XXXXXXXX)
        if phone.startswith('+'):
            phone = phone[1:]
        if phone.startswith('0'):
            phone = '254' + phone[1:]
            
        import base64
        import requests
        from requests.auth import HTTPBasicAuth
        from datetime import datetime
        from django.conf import settings
        from django.contrib import messages
        
        consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        shortcode = getattr(settings, 'MPESA_SHORTCODE', '174379')
        passkey = getattr(settings, 'MPESA_PASSKEY', '')
        callback_url = getattr(settings, 'MPESA_CALLBACK_URL', '')
        
        # 1. Authenticate to get OAuth Token
        token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        try:
            r = requests.get(token_url, auth=HTTPBasicAuth(consumer_key, consumer_secret), timeout=10)
            r.raise_for_status()
            access_token = r.json().get('access_token')
        except Exception as e:
            messages.error(request, f"M-Pesa Authentication Failed: {str(e)}. Please check MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET in settings.py.")
            return redirect('visit_bill', visit_id=bill.visit.id)
            
        # 2. Trigger STK Push
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = shortcode + passkey + timestamp
        password = base64.b64encode(password_str.encode('utf-8')).decode('utf-8')
        
        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        amount_val = int(payment_amount)
        
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount_val,
            "PartyA": phone,
            "PartyB": shortcode,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": f"INV-{bill.id}",
            "TransactionDesc": f"Hospital Bill payment for INV-{bill.id}"
        }
        
        try:
            stk_res = requests.post(stk_url, json=payload, headers=headers, timeout=10)
            stk_data = stk_res.json()
            response_code = stk_data.get('ResponseCode')
            response_description = stk_data.get('ResponseDescription', '')
            
            if response_code == '0':
                bill.amount_paid += payment_amount
                if bill.amount_paid + bill.discount >= bill.total_amount:
                    bill.is_paid = True
                    
                bill.generated_by = request.user
                bill.save()
                
                if bill.is_paid:
                    bill.visit.is_closed = True
                    bill.visit.save()
                    
                    # Auto-dispense prescriptions
                    for rx in bill.visit.prescriptions.filter(is_dispensed=False):
                        StockMovement.objects.create(
                            item=rx.item,
                            movement_type='OUT',
                            quantity=rx.quantity,
                            visit=bill.visit,
                            handled_by=request.user,
                            is_approved=True
                        )
                        rx.item.current_quantity -= rx.quantity
                        rx.item.save()
                        rx.is_dispensed = True
                        rx.save()
                        
                messages.success(request, f"STK Push sent successfully to {phone}! Please confirm on your phone to complete.")
            else:
                messages.error(request, f"M-Pesa STK Push Rejected: {response_description} (Code {response_code})")
        except Exception as e:
            messages.error(request, f"STK Push Request failed: {str(e)}")
            
        return redirect('visit_bill', visit_id=bill.visit.id)

@login_required
@role_required(['DOCTOR', 'ATTENDANT', 'PROPRIETOR'])
def bill_discharge(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    if request.method in ['POST', 'GET']:
        remaining = bill.total_amount - bill.discount - bill.amount_paid
        if remaining > 0:
            bill.amount_paid += remaining
            
        bill.is_paid = True
        bill.generated_by = request.user
        bill.save()
        
        bill.visit.is_closed = True
        bill.visit.save()
        
        # Auto-dispense prescriptions
        for rx in bill.visit.prescriptions.filter(is_dispensed=False):
            StockMovement.objects.create(
                item=rx.item,
                movement_type='OUT',
                quantity=rx.quantity,
                visit=bill.visit,
                handled_by=request.user,
                is_approved=True
            )
            rx.item.current_quantity -= rx.quantity
            rx.item.save()
            rx.is_dispensed = True
            rx.save()
            
        from django.contrib import messages
        messages.success(request, f"Patient discharged successfully. Bill marked as PAID.")
        return redirect('visit_bill', visit_id=bill.visit.id)
        
    return redirect('visit_bill', visit_id=bill.visit.id)
