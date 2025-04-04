from rest_framework import generics,viewsets,serializers
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem,InventoryHistory,Return,AuditLog
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
    
class StockSummaryView(generics.ListAPIView):
    queryset = Inventory.objects.all()
    serializer_class = serializers.InventorySerializer
    
    def get_queryset(self):
        return Inventory.objects.all().order_by('-total_quantity')
    
    
class ReceiptVS(viewsets.ModelViewSet):
    queryset = Receipt.objects.all().order_by('-creation_date')
    serializer_class = serializers.ReceiptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type','creation_date']
    
    
class ReceiptItemView(generics.ListCreateAPIView):
    queryset = ReceiptItem.objects.all()
    serializer_class = serializers.ReceiptItemSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        pk = self.request.data.get('receipt')
        receipt = get_object_or_404(Receipt, pk=pk)
        
        receipt_item = serializer.save(receipt=receipt)
        user = self.request.user if self.request.user.is_authenticated else None
        print(f"User: {self.request.user} (Authenticated: {self.request.user.is_authenticated})")
        
        
        for receipt_item in receipt.items.all():  
            purchase = receipt_item.purchase
            quantity = receipt_item.quantity
            item = receipt_item.purchase.item
            

            if receipt.type == Receipt.IMPORT:
                try:
                    inventory, created = Inventory.objects.get_or_create(item=item)
                    inventory.total_quantity += quantity
                    inventory.save()
                except Inventory.DoesNotExist:
                    raise ValidationError("Inventory record for this item does not exist!")
                InventoryHistory.objects.create(item=item,change_type =receipt.type,
                                                quantity_changed = quantity,
                                                receipt=receipt)
                

                AuditLog.objects.create(
                    action = AuditLog.IMPORT,
                    item = item,
                    quantity = quantity,
                    user = user,
                    receipt = receipt
                )
    
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
                
                AuditLog.objects.create(
                    action= AuditLog.EXPORT,
                    item = item,
                    quantity = quantity,
                    user = self.request.user,
                    receipt = receipt
                )
        
class ReceiptItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReceiptItem.objects.all()
    serializer_class = serializers.ReceiptItemSerializer
    
class InventoryHistoryListView(generics.ListAPIView):
    queryset = InventoryHistory.objects.all().order_by('-timestamp')
    serializer_class = serializers.InventoryHistorySerializer
    
class ReturnCreateView(generics.ListCreateAPIView):
    queryset = Return.objects.all()
    serializer_class = serializers.ReturnSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        return_item = serializer.save()
        receipt_item = return_item.receipt_item
        receipt = receipt_item.receipt
        inventory = Inventory.objects.get(item=receipt_item.purchase.item)
        
        if return_item.quantity_returned > receipt_item.quantity:
            raise ValidationError("The returned quantity cannot exceed the exported quantity!")
        print(f" Return Item Quantity: {return_item.quantity_returned}")
        
        user = self.request.user if self.request.user.is_authenticated else None
        print(f"User: {self.request.user} (Authenticated: {self.request.user.is_authenticated})")
        
        if receipt.type == Receipt.IMPORT:
            if inventory.total_quantity < return_item.quantity_returned:
                raise ValidationError("Cannot return more than available inventory!")
            
            receipt_item.quantity -= return_item.quantity_returned
            receipt_item.save()
            
            inventory.total_quantity -= return_item.quantity_returned
            inventory.save()
            
            AuditLog.objects.create(
                action = AuditLog.RETURN,
                item = receipt_item.purchase.item,
                quantity = return_item.quantity_returned,
                user = user,
                receipt = receipt
            )
            
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
        
        

        AuditLog.objects.create(
            action = AuditLog.RETURN,
            item = receipt_item.purchase.item,
            quantity = return_item.quantity_returned,
            user = user,
            receipt = receipt
        )

        
    
class ReturnHistoryView(generics.ListAPIView):
    queryset = Return.objects.all().order_by('-return_date')
    serializer_class = serializers.ReturnSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['receipt_item__receipt__type','receipt_item__purchase__item','quantity_returned','return_date']
        
class ReturnDetailView(generics.RetrieveAPIView):
    queryset = Return.objects.all()
    serializer_class = serializers.ReturnSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    
class ExpiringSoonView(generics.ListAPIView):
    serializer_class = serializers.PurchaseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        days = self.request.query_params.get('days', 30)
        try:
            days = int(days)
        except ValueError:
            raise serializers.ValidationError({"days": "Invalid number"})
        expire_date = now().date() + timedelta(days=days)
        return Purchase.objects.filter(expiration_date__lte = expire_date).order_by('expiration_date')


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = serializers.AuditLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['action','item','user','timestamp']