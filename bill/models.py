from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from case.models import Visit, ServiceRecord, Prescription
from stock.models import StockMovement, StockItem
from decimal import Decimal

class Bill(models.Model):
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)

class Expense(models.Model):
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    logged_by = models.ForeignKey(User, on_delete=models.PROTECT)

class OTCSale(models.Model):
    item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    sold_by = models.ForeignKey(User, on_delete=models.PROTECT)

@receiver(post_save, sender=ServiceRecord)
def auto_update_bill(sender, instance, created, **kwargs):
    if created:
        bill, created_bill = Bill.objects.get_or_create(visit=instance.visit)
        bill.total_amount = Decimal(str(bill.total_amount)) + (instance.applied_price * instance.quantity)
        bill.save()

@receiver(post_save, sender=Prescription)
def auto_update_bill_from_prescription(sender, instance, created, **kwargs):
    if created:
        bill, created_bill = Bill.objects.get_or_create(visit=instance.visit)
        # Charge the patient the selling price of the item * quantity prescribed
        bill.total_amount = Decimal(str(bill.total_amount)) + (instance.item.unit_price * instance.quantity)
        bill.save()
