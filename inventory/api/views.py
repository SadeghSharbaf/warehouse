from rest_framework import generics,viewsets,serializers
from rest_framework.exceptions import ValidationError
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem,InventoryHistory,Return
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
            
            InventoryHistory.objects.create(item=item,change_type = Receipt.IMPORT,
                                            quantity_changed = quantity)
        
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
            
            InventoryHistory.objects.create(item=item, change_type = Receipt.EXPORT,
                                            quantity_changed = quantity)
        
class ReceiptItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReceiptItem.objects.all()
    serializer_class = serializers.ReceiptItemSerializer
    
class InventoryHistoryListView(generics.ListAPIView):
    queryset = InventoryHistory.objects.all().order_by('-timestamp')
    serializer_class = serializers.InventoryHistorySerializer
    
class ReturnCreateView(generics.ListCreateAPIView):
    queryset = Return.objects.all()
    serializer_class = serializers.ReturnSerializer
    
    def perform_create(self, serializer):
        return_item = serializer.save()
        receipt_item = return_item.receipt_item
        receipt = receipt_item.receipt
        inventory = Inventory.objects.get(item=receipt_item.purchase.item)
        
        if return_item.quantity_returned > receipt_item.quantity:
            raise ValidationError("The returned quantity cannot exceed the exported quantity!")
        print(f" Return Item Quantity: {return_item.quantity_returned}")
        
        if receipt.type == Receipt.IMPORT:
            receipt_item.quantity -= return_item.quantity_returned
            receipt_item.save()
            
            inventory.total_quantity -= return_item.quantity_returned
            inventory.save()
            
        elif receipt.type == Receipt.EXPORT:
            
            receipt_item.quantity -= return_item.quantity_returned
            receipt_item.save()
        
            inventory.total_quantity += return_item.quantity_returned
            inventory.save()
        print(f"After Update: {inventory.total_quantity}")

        
class ReturnDetailView(generics.RetrieveAPIView):
    queryset = Return.objects.all()
    serializer_class = serializers.ReturnSerializer