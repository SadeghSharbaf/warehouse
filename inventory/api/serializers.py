from rest_framework import serializers
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem,InventoryHistory,Return,AuditLog
from rest_framework.exceptions import ValidationError

class ItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Item
        fields = "__all__"
        
        
class PurchaseSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    
    class Meta:
        model = Purchase
        fields = "__all__"

        
class InventorySerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    
    class Meta:
        model = Inventory
        fields = "__all__"
        
        
class ReceiptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Receipt
        fields = "__all__"
        
        
class ReceiptItemSerializer(serializers.ModelSerializer):
    purchase_name = serializers.CharField(source='purchase.item.name', read_only=True)
    receipt_type = serializers.CharField(source = 'receipt.type',read_only = True)
    
    class Meta:
        model = ReceiptItem
        fields = "__all__"
        
        
    def create(self,validated_data):
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        
        receipt = validated_data['receipt']
        purchase = validated_data['purchase']
        quantity = validated_data['quantity']
        item = purchase.item
        
        receipt_item = ReceiptItem.objects.create(**validated_data)
        
        if receipt.type == Receipt.IMPORT:
            inventory, created = Inventory.objects.get_or_create(item=item)
            inventory.total_quantity += quantity
            inventory.save()
            
            InventoryHistory.objects.create(
                item  =item,
                receipt = receipt,
                change_type = Receipt.IMPORT,
                quantity_changed = quantity
            )
            
            AuditLog.objects.create(
                action = AuditLog.IMPORT,
                quantity = quantity,
                item = item,
                receipt = receipt,
                user = user
            )
            
        elif receipt.type == Receipt.EXPORT:
            inventory = Inventory.objects.get(item = item)
            if inventory.total_quantity < quantity :
                raise serializers.ValidationError("Inventory is not enough!")
            
            purchases = Purchase.objects.all().order_by('expiration_date')
            quantity_to_deduct = quantity
            
            for purchase in purchases:
                if quantity_to_deduct < 0:
                    break
                if purchase.quantity >= quantity_to_deduct:
                    purchase.quantity -= quantity_to_deduct
                    purchase.save()
                    quantity_to_deduct = 0
                else :
                    quantity_to_deduct -= purchase.quantity
                    purchase.quantity = 0 
                    purchase.save()
                    
            inventory.total_quantity -= quantity
            inventory.save()
            
            
            InventoryHistory.objects.create(
                item  = item,
                receipt = receipt,
                change_type = Receipt.EXPORT,
                quantity_changed = quantity
            )
            
            
            AuditLog.objects.create(
                action = AuditLog.EXPORT,
                item = item ,
                quantity = quantity,
                receipt = receipt,
                user = user
            )
        
        return receipt_item
        
class InventoryHistorySerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source = "item.name", read_only = True)
    receipt_id = serializers.CharField(source = "receipt.id",read_only = True)
    purchase_id = serializers.CharField(source = "purchase.id",read_only = True)
    change_type = serializers.CharField(read_only = True)
    quantity_changed = serializers.IntegerField(read_only = True)
    timestamp = serializers.DateTimeField(read_only = True)
    
    class Meta:
        model = InventoryHistory
        fields = ["receipt_id", "purchase_id", "item_name", "change_type", "quantity_changed", "timestamp"]
        
        
class ReturnSerializer(serializers.ModelSerializer):
    receipt_item_datail = serializers.CharField(source = "receipt_item.purchase.item.name", read_only = True)
    
    class Meta:
        model = Return
        fields = ["id", "receipt_item", "receipt_item_datail", "quantity_returned", "return_date"]
        
        

class AuditLogSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source = "item.name", read_only = True)
    user_name = serializers.CharField(source = "user.username", read_only = True)
    
    class Meta:
        model = AuditLog
        fields = "__all__"