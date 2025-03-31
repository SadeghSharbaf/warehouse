from rest_framework import generics,viewsets,serializers
from rest_framework.exceptions import ValidationError
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem,InventoryHistory,Return,
from inventory.api import serializers
from django.shortcuts import get_object_or_404
from django.utils.timezone import now,timedelta

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
    queryset = Receipt.objects.all().order_by('-creation_date')
    serializer_class = serializers.ReceiptSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        receipt_type = self.request.query_params.get('type')
        
        if receipt_type:
            queryset = queryset.filter(type=receipt_type)
            
        return queryset
    
    
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
            
            InventoryHistory.objects.create(item=item,change_type =receipt.type,
                                            quantity_changed = quantity,
                                            receipt=receipt)
        
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
                    quantity_to_deduct -= purchase.quantity
                    purchase.quantity = 0
                    purchase.save()
            
            inventory.total_quantity -= quantity
            inventory.save()
            
            InventoryHistory.objects.create(item=item, change_type = receipt.type,
                                            quantity_changed = quantity,
                                            receipt=receipt)
        
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
            if inventory.total_quantity < return_item.quantity_returned:
                raise ValidationError("Cannot return more than available inventory!")
            
            receipt_item.quantity -= return_item.quantity_returned
            receipt_item.save()
            
            inventory.total_quantity -= return_item.quantity_returned
            inventory.save()
            
        elif receipt.type == Receipt.EXPORT:
            
            receipt_item.quantity -= return_item.quantity_returned
            receipt_item.save()
        
            inventory.total_quantity += return_item.quantity_returned
            inventory.save()
            
        InventoryHistory.objects.create(receipt=receipt,
                                        item=receipt_item.purchase.item,
                                        change_type="return",
                                        quantity_changed=return_item.quantity_returned)
        print(f"After Update: {inventory.total_quantity}")
        

class ReceiptHistoryView(generics.ListAPIView):
    queryset = Return.objects.all().order_by('-return_date')
    serializer_class = serializers.ReturnSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        receipt_id = self.request.query_params.get('receipt')
        
        if receipt_id:
            queryset = queryset.filter(receipt_item__receipt_id = receipt_id)
        return queryset
    

        
class ReturnDetailView(generics.RetrieveAPIView):
    queryset = Return.objects.all()
    serializer_class = serializers.ReturnSerializer
    
class ExpiringSoonView(generics.ListAPIView):
    serializer_class = serializers.PurchaseSerializer
    
    def get_queryset(self):
        expire_date = now().date() + timedelta(days=30)
        return Purchase.objects.filter(expiration_date__lte = expire_date).order_by('expiration_date')
