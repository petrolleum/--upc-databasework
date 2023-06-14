from django.contrib import admin
from .models import Staff,Gas_category,Supplier,Deliery_staff,Gas_in,Gas_out,Customer
# Register your models here.
admin.site.register(Staff)
admin.site.register(Gas_category)
admin.site.register(Supplier)
admin.site.register(Deliery_staff)
admin.site.register(Gas_in)
admin.site.register(Gas_out)
admin.site.register(Customer)

