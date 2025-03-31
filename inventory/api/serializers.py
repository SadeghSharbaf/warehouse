from rest_framework import serializers
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem,InventoryHistory,Return

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
        fields = "__all__"