from django.contrib import admin

# Register your models here.
from . import models
admin.site.register(models.User)
admin.site.register(models.Truck)
admin.site.register(models.Package)
admin.site.register(models.Product)