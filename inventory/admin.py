from django.contrib import admin
from .models import Item,Purchase,Inventory

admin.site.register(Item)
admin.site.register(Purchase)
admin.site.register(Inventory)