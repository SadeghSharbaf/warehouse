from rest_framework import generics,viewsets,serializers
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem
from inventory.api import serializers
from django.shortcuts import get_object_or_404

class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer
    
class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer
    

class PurchaseCreateView(generics.ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer
    
class PurchaseDetailView(generics.RetrieveAPIView):
    queryset = Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer
    
class InventoryListView(generics.ListAPIView):
    queryset = Inventory.objects.all()
    serializer_class = serializers.InventorySerializer
    
class ReceiptVS(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer
    
class ReceiptItemView(generics.ListCreateAPIView):
    queryset = ReceiptItem.objects.all()
    serializer_class = serializers.ReceiptItemSerializer
    
    def perform_create(self, serializer):
        pk = self.request.data.get('receipt')
        receipt = get_object_or_404(Receipt, pk=pk)
        
        receipt_item = serializer.save(receipt=receipt)
        purchase = receipt_item.purchase
        quantity = receipt_item.quantity
        item = receipt_item.purchase.item
        
        if receipt.type == Receipt.IMPORT:
            inventory, created = Inventory.objects.get_or_create(item=item)
            inventory.total_quantity += quantity
            inventory.save()
        
        elif receipt.type == Receipt.EXPORT:
            quantity_to_deduct = quantity
            purchases = Purchase.objects.filter(item=item).order_by('expiration_date')
            
            inventory = Inventory.objects.get(item=item)
            if inventory.total_quantity < quantity:
                raise serializers.ValidationError("inventory is not enough!")
            for purchase in purchases:
                if quantity_to_deduct <= 0 :
                    break
                
                if purchase.quantity >= quantity_to_deduct:
                    purchase.quantity -= quantity_to_deduct
                    purchase.save()
                    quantity_to_deduct = 0
                else:
                    quantity_to_deduct -= quantity
                    purchase.quantity = 0
                    purchase.save()
            
            inventory.total_quantity -= quantity
            inventory.save()
        
class ReceiptItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReceiptItem.objects.all()
    serializer_class = serializers.ReceiptItemSerializer