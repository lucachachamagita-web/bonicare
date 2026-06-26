from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from profiles.permissions import role_required
from bill.models import Bill, Expense, OTCSale
from case.models import ServiceRecord
from stock.models import StockMovement, StockItem
from profiles.models import SalaryRecord
from django.db.models import Sum, Count, F
from django.utils import timezone

@login_required
@role_required(['PROPRIETOR'])
def proprietor_dashboard(request):
    today = timezone.now().date()
    first_of_month = today.replace(day=1)
    
    # --- Daily Snapshot ---
    daily_revenue_bills = Bill.objects.filter(generated_at__date=today, is_paid=True).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    daily_revenue_otc = OTCSale.objects.filter(timestamp__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    daily_revenue = daily_revenue_bills + daily_revenue_otc
    
    daily_expenses_explicit = Expense.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    daily_stock_movements = StockMovement.objects.filter(movement_type='IN', is_approved=True, timestamp__date=today)
    daily_stock_expense = sum((m.quantity * (m.cost_price or 0)) for m in daily_stock_movements)
    daily_expenses = daily_expenses_explicit + daily_stock_expense
    
    # --- Monthly P&L ---
    monthly_revenue_bills = Bill.objects.filter(generated_at__date__gte=first_of_month, is_paid=True).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    monthly_revenue_otc = OTCSale.objects.filter(timestamp__date__gte=first_of_month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = monthly_revenue_bills + monthly_revenue_otc
    
    monthly_expenses_explicit = Expense.objects.filter(date__gte=first_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_stock_movements = StockMovement.objects.filter(movement_type='IN', is_approved=True, timestamp__date__gte=first_of_month)
    monthly_stock_expense = sum((m.quantity * (m.cost_price or 0)) for m in monthly_stock_movements)
    monthly_salaries = SalaryRecord.objects.filter(month__gte=first_of_month, is_paid=True)
    monthly_salary_expense = sum((s.base_salary + s.bonus) for s in monthly_salaries)
    
    monthly_expenses = monthly_expenses_explicit + monthly_stock_expense + monthly_salary_expense
    profit = monthly_revenue - monthly_expenses
    
    # Top Services
    top_services = ServiceRecord.objects.values('service__name').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Top Medicines
    top_medicines = StockMovement.objects.filter(movement_type='OUT').values('item__name').annotate(qty=Sum('quantity')).order_by('-qty')[:5]
    
    # Auto-Generated Order List
    order_list = StockItem.objects.filter(current_quantity__lte=F('reorder_level'))
    
    context = {
        'daily_revenue': daily_revenue,
        'daily_expenses': daily_expenses,
        'monthly_revenue': monthly_revenue,
        'monthly_expenses': monthly_expenses,
        'profit': profit,
        'top_services': top_services,
        'top_medicines': top_medicines,
        'order_list': order_list,
    }
    return render(request, 'reports/proprietor_dashboard.html', context)

@login_required
@role_required(['PROPRIETOR'])
def cash_flow_report(request):
    today = timezone.now().date()
    first_of_month = today.replace(day=1)
    
    bills = Bill.objects.filter(generated_at__date__gte=first_of_month, is_paid=True).order_by('-generated_at')
    otc_sales = OTCSale.objects.filter(timestamp__date__gte=first_of_month).order_by('-timestamp')
    
    # --- Income Calculation ---
    total_revenue_bills = bills.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_revenue_otc = otc_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_revenue = total_revenue_bills + total_revenue_otc
    
    service_breakdown = []
    prescription_breakdown = []
    
    for bill in bills:
        for srv in bill.visit.services.all():
            service_breakdown.append({
                'date': bill.generated_at,
                'patient': f"{bill.visit.patient.first_name} {bill.visit.patient.last_name}",
                'name': srv.service.name,
                'amount': srv.applied_price * srv.quantity
            })
        for rx in bill.visit.prescriptions.all():
            prescription_breakdown.append({
                'date': bill.generated_at,
                'patient': f"{bill.visit.patient.first_name} {bill.visit.patient.last_name}",
                'name': rx.item.name,
                'amount': rx.item.unit_price * rx.quantity
            })
            
    # --- Expenses Calculation ---
    expenses = Expense.objects.filter(date__gte=first_of_month).order_by('-date')
    stock_ins = StockMovement.objects.filter(movement_type='IN', is_approved=True, timestamp__date__gte=first_of_month)
    salaries = SalaryRecord.objects.filter(month__gte=first_of_month, is_paid=True)
    
    total_expenses_explicit = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_stock_expense = sum((m.quantity * (m.cost_price or 0)) for m in stock_ins)
    total_salary_expense = sum((s.base_salary + s.bonus) for s in salaries)
    total_expenses = total_expenses_explicit + total_stock_expense + total_salary_expense
    
    stock_purchases = []
    for m in stock_ins:
        stock_purchases.append({
            'date': m.timestamp,
            'item': m.item.name,
            'quantity': m.quantity,
            'cost': m.quantity * (m.cost_price or 0)
        })
        
    salary_payouts = []
    for s in salaries:
        salary_payouts.append({
            'month': s.month,
            'employee': s.employee.username,
            'amount': s.base_salary + s.bonus
        })
    
    net_profit = total_revenue - total_expenses
    
    return render(request, 'reports/cash_flow_report.html', {
        'total_revenue': total_revenue,
        'total_revenue_bills': total_revenue_bills,
        'total_revenue_otc': total_revenue_otc,
        
        'total_expenses': total_expenses,
        'total_expenses_explicit': total_expenses_explicit,
        'total_stock_expense': total_stock_expense,
        'total_salary_expense': total_salary_expense,
        
        'net_profit': net_profit,
        'month': first_of_month.strftime('%B %Y'),
        
        'otc_sales': otc_sales,
        'service_breakdown': service_breakdown,
        'prescription_breakdown': prescription_breakdown,
        'expenses': expenses,
        'stock_purchases': stock_purchases,
        'salary_payouts': salary_payouts,
    })

@login_required
@role_required(['PROPRIETOR'])
def orders_report(request):
    order_list = StockItem.objects.filter(current_quantity__lte=F('reorder_level')).order_by('name')
    return render(request, 'reports/orders_report.html', {'order_list': order_list})

@login_required
@role_required(['PROPRIETOR'])
def stock_flow_report(request):
    movements = StockMovement.objects.all().order_by('-timestamp')[:200]
    return render(request, 'reports/stock_flow_report.html', {'movements': movements})
