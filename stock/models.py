from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from case.models import Visit

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=50)

class StockItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[('MEDICINE', 'Medicine'), ('CONSUMABLE', 'Consumable')])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Selling price
    current_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)

class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    delivery_note_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('RECEIVED', 'Received')])
    ordered_date = models.DateTimeField(auto_now_add=True)
    received_date = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)

class StockMovement(models.Model):
    item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=10, choices=[('IN', 'Stock In'), ('OUT', 'Dispensed')])
    quantity = models.IntegerField()
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, null=True, blank=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    handled_by = models.ForeignKey(User, on_delete=models.PROTECT)
    is_approved = models.BooleanField(default=False)
    is_otc = models.BooleanField(default=False)

    def clean(self):
        if self.movement_type == 'OUT' and not self.visit and not self.is_otc:
            raise ValidationError("Stock OUT must be linked to a Patient Visit or be an OTC Sale.")
        if self.movement_type == 'IN' and not self.purchase_order:
            raise ValidationError("Stock IN must be linked to a Purchase Order with a Delivery Note.")
        
        # Enforce Delivery Note
        if self.movement_type == 'IN' and self.purchase_order and not self.purchase_order.delivery_note_number:
            raise ValidationError("Cannot move stock IN without a Delivery Note on the Purchase Order.")
