from django.contrib import admin
from .models import Supplier, StockItem, PurchaseOrder, StockMovement

admin.site.register(Supplier)
admin.site.register(StockItem)
admin.site.register(PurchaseOrder)
admin.site.register(StockMovement)
