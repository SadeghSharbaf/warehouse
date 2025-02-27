from rest_framework import serializers
from inventory.models import Item,Purchase,Inventory

class ItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Item
        fields = "__all__"
        
class PurchaseSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())
    
    class Meta:
        model = Purchase
        fields = "__all__"
        
class InventorySerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    
    class Meta:
        model = Inventory
        fields = "__all__"