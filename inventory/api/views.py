from rest_framework import generics,viewsets,serializers,status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem,InventoryHistory,Return,AuditLog
from inventory.api import serializers
from django.shortcuts import get_object_or_404
from django.utils.timezone import now,timedelta
from django.db.models import Sum

class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAuthenticated]
    
class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAuthenticated]
    

class PurchaseCreateView(generics.ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer
    permission_classes = [IsAuthenticated]
    
class PurchaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer
    permission_classes = [IsAuthenticated]
    
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
    
    def create(self, request, *args, **kwargs):
        Is_bulk = isinstance(request.data , list)
        
        serializer = self.get_serializer(data=request.data , many = Is_bulk)
        serializer.is_valid(raise_exception = True)
        
        if Is_bulk:
            instances =[]
            for item_data in request.data:
                item_serializer = self.serializer_class(data=item_data, context= {"request":request})
                item_serializer.is_valid(raise_exception=True)
                instance = item_serializer.save()
                instances.append(instance)
            data = self.get_serializer(instances, many=True).data
            
        else :
            serializer = self.get_serializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer)
            data = self.get_serializer(instance).data
            
        
        return Response(data,status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        return serializer.save()
    

        
class ReceiptItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReceiptItem.objects.all()
    serializer_class = serializers.ReceiptItemSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        item = instance.purchase.item
        quantity = instance.quantity
        receipt = instance.receipt
        
        inventory = Inventory.objects.get(item=item)
        
        if receipt.type == Receipt.IMPORT:
            if inventory.total_quantity < quantity:
                raise ValidationError("Cannot delete. Inventory would go negative.")
            
            inventory.total_quantity -= quantity
            
            
        elif receipt.type == Receipt.EXPORT:
            inventory.total_quantity += quantity
            
            quantity_to_return = quantity
            purchases = Purchase.objects.filter(item=item).order_by('expiration_date')
            
            for purchase in purchases:
                if quantity_to_return <= 0:
                    break
                
                purchase.quantity += quantity_to_return
                purchase.save()
                quantity_to_return = 0
            
        inventory.save()
        
        InventoryHistory.objects.create(
            item  = item,
            receipt = receipt,
            change_type = InventoryHistory.DELETE,
            quantity_changed = quantity if receipt.type == Receipt.EXPORT else f"-{quantity}"
            )
            
            
        AuditLog.objects.create(
            action = F"DELETE_{receipt.type}",
            item = item ,
            quantity = quantity,
            receipt = receipt,
            user = user
        )
        return super().destroy(request, *args, **kwargs)
    
class InventoryHistoryListView(generics.ListAPIView):
    queryset = InventoryHistory.objects.all().order_by('-timestamp')
    serializer_class = serializers.InventoryHistorySerializer
    permission_classes = [AllowAny]
    
class ReturnCreateView(generics.ListCreateAPIView):
    queryset = Return.objects.all()
    serializer_class = serializers.ReturnSerializer
    permission_classes = [IsAuthenticated]
    
    
    def create(self, request, *args, **kwargs):
        is_bulk = isinstance(request.data, list)
        print("Request data:", request.data) 
        serializer =self.get_serializer(data=request.data, many=is_bulk)
        serializer.is_valid(raise_exception=True)
        
        if is_bulk:
            created_returns =[]
            for item_data in request.data:
                item_serializer = self.get_serializer(data=item_data, context={"request": request})
                item_serializer.is_valid(raise_exception=True)
                created_return = self.handle_return(item_serializer.validated_data)
                created_returns.append(created_return)
                
            reasponse_data = self.get_serializer(created_returns, many=True, context={"request": request}).data
                
        else:
            created_return = self.handle_return(serializer.validated_data)
            print("Created return instance (repr):", created_return)
            print("Receipt item:", created_return.receipt_item)
            print("Quantity returned:", created_return.quantity_returned)

            reasponse_data = self.get_serializer(created_return).data
                
        return Response(reasponse_data,status=status.HTTP_201_CREATED)
        
        
    def handle_return(self, validated_data):
        return_item = Return.objects.create(**validated_data)
        print(f"Created return: {return_item}")
        receipt_item = return_item.receipt_item
        receipt = receipt_item.receipt
        item = receipt_item.purchase.item
        inventory = Inventory.objects.get(item=item)
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        
        total_return = Return.objects.filter(receipt_item=receipt_item).aggregate(total=Sum('quantity_returned'))['total'] or 0

        if receipt.type == Receipt.IMPORT:
            if total_return  > receipt_item.quantity:
                print(f"Exceeded exported quantity: total_return({total_return}) + return_item.quantity_returned({return_item.quantity_returned}) > receipt_item.quantity({receipt_item.quantity})")
                raise ValidationError("The returned quantity cannot exceed the exported quantity!")
        
            if inventory.total_quantity < return_item.quantity_returned:
                raise ValidationError("Cannot return more than available inventory!")
            
            receipt_item.quantity -= return_item.quantity_returned
            inventory.total_quantity -= return_item.quantity_returned
            
        elif receipt.type == Receipt.EXPORT:
            if total_return + return_item.quantity_returned > receipt_item.quantity:
                raise ValidationError("The returned quantity cannot exceed the exported quantity!")
            receipt_item.quantity -= return_item.quantity_returned
            inventory.total_quantity += return_item.quantity_returned
            
        receipt_item.save()
        inventory.save()
        
        InventoryHistory.objects.create(
            receipt=receipt,
            item=item,
            change_type="return",
            quantity_changed=return_item.quantity_returned
        )
        
        
        
        AuditLog.objects.create(
            action=AuditLog.RETURN,
            item=item,
            quantity=return_item.quantity_returned,
            user=user,
            receipt=receipt
        )
        
        return return_item
    

    
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