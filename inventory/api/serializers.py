from rest_framework import serializers
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem

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
    
    class Meta:
        model = ReceiptItem
        fields = "__all__"