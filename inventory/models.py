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
    item = models.ForeignKey(Item, verbose_name="Item", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(blank=True,null=True)
    
    def __str__(self):
        return f"{self.quantity} {self.item.unit} of {self.item.name}"
    
class Inventory(models.Model):
    item = models.OneToOneField(Item, verbose_name="item", on_delete=models.CASCADE)
    total_quantity = models.PositiveIntegerField(default=0,editable=True)
    
    def __str__(self):
        return f"{self.item.name}: {self.total_quantity} {self.item.unit}"
    

class Receipt(models.Model):
    IMPORT = 'import'
    EXPORT = 'export'
    
    TYPE_CHOICES =[
        (IMPORT,'import'),
        (EXPORT,'export')
    ]
    type = models.CharField(max_length=15,choices=TYPE_CHOICES)
    creation_date = models.DateTimeField(auto_now_add=True)
    optional_notes = models.TextField(blank=True,null=True)
    
    def __str__(self):
        return f"{self.type} Receipt {self.pk}"
    
    
class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt,verbose_name="receipt", on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase,verbose_name="purchase", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
class InventoryHistory(models.Model):
    IMPORT = 'import'
    EXPORT = 'export'
    
    TYPE_CHOICES =[
        (IMPORT,'import'),
        (EXPORT,'export')
    ]
    item = models.ForeignKey(Item, verbose_name=("item"), on_delete=models.CASCADE,related_name="history")
    receipt =models.ForeignKey(Receipt, verbose_name=("receipt"), on_delete=models.CASCADE)
    change_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity_changed = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.item.name} - {self.change_type} - {self.quantity_changed} - {self.timestamp}"
    
    
class Return(models.Model):
    receipt_item = models.ForeignKey(ReceiptItem, verbose_name=("receipt-item"), on_delete=models.CASCADE)
    quantity_returned = models.PositiveIntegerField(default=0)
    return_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"from return{self.id} - {self.quantity_returned} {self.receipt_item.purchase.item.name} on {self.return_date.strftime('%Y-%m-%d %H:%M')}"
    
    
class AuditLog(models.Model):
    
    IMPORT = 'import'
    EXPORT = 'export'
    RETURN = 'return'
    PURCHASE = 'purchase'
    action_choises = [
        ('import', IMPORT),
        ('export', EXPORT),
        ('return', RETURN),
        ('purchase', PURCHASE)
    ]
    
    action = models.CharField(max_length=15, choices=action_choises)
    item = models.ForeignKey(Item, verbose_name=("item"), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add = True)
    user = models.ForeignKey(User, verbose_name=("user"), on_delete=models.CASCADE,blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_action_display()} : {self.user.name} ({self.quantity})"