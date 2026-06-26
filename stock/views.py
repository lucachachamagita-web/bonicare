from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StockItem, StockMovement, PurchaseOrder
from case.models import Visit
from bill.models import OTCSale
from profiles.permissions import role_required
from django.core.exceptions import ValidationError

@login_required
@role_required(['PROPRIETOR', 'DOCTOR', 'ATTENDANT'])
def stock_list(request):
    items = StockItem.objects.all().order_by('name')
    return render(request, 'stock/stock_list.html', {'items': items})

@login_required
@role_required(['PROPRIETOR', 'DOCTOR'])
def stock_item_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        unit_price = request.POST.get('unit_price', '0.00')
        reorder_level = request.POST.get('reorder_level', '10')
        
        StockItem.objects.create(
            name=name,
            category=category,
            unit_price=unit_price,
            reorder_level=reorder_level,
            current_quantity=0,
            cost_price='0.00'
        )
        return redirect('stock_list')
        
    return render(request, 'stock/stock_item_form.html')

@login_required
@role_required(['DOCTOR', 'ATTENDANT'])
def stock_movement(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        po_id = request.POST.get('po_id')
        
        item = StockItem.objects.get(id=item_id)
        purchase_order = PurchaseOrder.objects.get(id=po_id) if po_id else None
        
        try:
            mov = StockMovement(
                item=item,
                movement_type='IN',
                quantity=quantity,
                purchase_order=purchase_order,
                handled_by=request.user
            )
            
            cost_price = request.POST.get('cost_price')
            selling_price = request.POST.get('selling_price')
            if cost_price:
                mov.cost_price = cost_price
                item.cost_price = cost_price
            if selling_price:
                mov.selling_price = selling_price
                item.unit_price = selling_price
            mov.clean()
            mov.save()
            item.save()
            
            return redirect('stock_list')
        except ValidationError as e:
            return render(request, 'stock/movement_form.html', {
                'error': e.messages[0],
                'items': StockItem.objects.all(),
                'pos': PurchaseOrder.objects.filter(status='PENDING', is_approved=True)
            })
            
    items = StockItem.objects.all()
    pos = PurchaseOrder.objects.filter(status='PENDING', is_approved=True)
    return render(request, 'stock/movement_form.html', {'items': items, 'pos': pos})

@login_required
@role_required(['ATTENDANT', 'PROPRIETOR', 'DOCTOR'])
def otc_sale_create(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        item = StockItem.objects.get(id=item_id)
        
        if quantity > item.current_quantity:
            return render(request, 'stock/otc_sale_form.html', {
                'error': f'Not enough stock. Only {item.current_quantity} available.',
                'items': StockItem.objects.filter(current_quantity__gt=0)
            })
        
        total = item.unit_price * quantity
        
        # Create OTC Sale
        sale = OTCSale.objects.create(
            item=item,
            quantity=quantity,
            total_amount=total,
            sold_by=request.user
        )
        
        # Create Stock OUT movement
        mov = StockMovement.objects.create(
            item=item,
            movement_type='OUT',
            quantity=quantity,
            handled_by=request.user,
            is_otc=True,
            is_approved=True # Auto-approved since it's paid
        )
        
        item.current_quantity -= quantity
        item.save()
        
        return render(request, 'stock/otc_receipt.html', {'sale': sale})
        
    items = StockItem.objects.filter(current_quantity__gt=0)
    return render(request, 'stock/otc_sale_form.html', {'items': items})

@login_required
@role_required(['PROPRIETOR'])
def stock_approvals(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        obj_id = request.POST.get('obj_id')
        
        if action == 'approve_po':
            po = PurchaseOrder.objects.get(id=obj_id)
            po.is_approved = True
            po.save()
        elif action == 'verify_in':
            mov = StockMovement.objects.get(id=obj_id)
            mov.is_approved = True
            mov.save()
            # Update quantity now that Proprietor verified it
            mov.item.current_quantity += mov.quantity
            mov.item.save()
            
        return redirect('stock_approvals')
        
    pending_pos = PurchaseOrder.objects.filter(is_approved=False).order_by('-ordered_date')
    unverified_ins = StockMovement.objects.filter(movement_type='IN', is_approved=False).order_by('-timestamp')
    
    return render(request, 'stock/stock_approvals.html', {
        'pending_pos': pending_pos,
        'unverified_ins': unverified_ins
    })
