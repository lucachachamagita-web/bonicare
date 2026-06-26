from django.contrib import admin
from .models import Visit, ServiceCatalog, ServiceRecord

admin.site.register(Visit)
admin.site.register(ServiceCatalog)
admin.site.register(ServiceRecord)
