from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description =models.TextField(blank=True,null=True)
    unit = models.CharField(max_length=63) #for pieces,kilograms etc...
    
    def __str__(self):
        return self.name
    
class Purchase(models.Model):
    item = models.ForeignKey(Item, verbose_name=("Item"), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(blank=True,null=True)
    
    def __str__(self):
        return f"{self.quantity} {self.item.unit} of {self.item.name}"
    
class Inventory(models.Model):
    item = models.OneToOneField(Item, verbose_name=("item"), on_delete=models.CASCADE)
    total_quantity = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.item.name}: {self.total_quantity} {self.item.unit}"