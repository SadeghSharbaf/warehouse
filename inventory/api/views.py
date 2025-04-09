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
    
class InventoryHistoryListView(generics.ListAPIView):
    queryset = InventoryHistory.objects.all().order_by('-timestamp')
    serializer_class = serializers.InventoryHistorySerializer
    
class ReturnCreateView(generics.ListCreateAPIView):
    queryset = Return.objects.all()
    serializer_class = serializers.ReturnSerializer
    permission_classes = [IsAuthenticated]
    
    
    def create(self, request, *args, **kwargs):
        is_bulk = isinstance(request.data, list)
        serializer =self.get_serializer(data=request.data, many=is_bulk, context={"request":request})
        serializer.is_valid(raise_exception=True)
        
        if is_bulk:
            created_returns =[]
            for item_data in request.data:
                item_serializer = self.get_serializer(data=item_data, context={"request": request})
                item_serializer.is_valid(raise_exception=True)
                created_return = self.handel_return(item_serializer.validated_data)
                created_returns.append(created_return)
            reasponse_data = self.get_serializer(created_returns, many=True).data
                
        else:
            created_return = self.handle_return(serializer.validated_data)
            reasponse_data = self.get_serializer(created_return).data
                
        return Response(reasponse_data,status=status.HTTP_201_CREATED)
        
        
    def handle_return(self, validated_data):
        return_item = Return.objects.create(**validated_data)
        receipt_item = return_item.receipt_item
        receipt = receipt_item.receipt
        item = receipt_item.purchase.item
        inventory = Inventory.objects.get(item=item)
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        
        total_return = Return.objects.filter(receipt_item=receipt_item).aggregate(total=models.Sum('quantity_returned'))['total'] or 0
        if total_return + return_item.quantity_returned > receipt_item.quantity:
            raise ValidationError("The returned quantity cannot exceed the exported quantity!")
        
        if receipt.type == Receipt.IMPORT:
            if inventory.total_quantity < return_item.quantity_returned:
                raise ValidationError("Cannot return more than available inventory!")
            
            receipt_item.quantity -= return_item.quantity_returned
            inventory.total_quantity -= return_item.quantity_returned
            
        elif receipt.type == Receipt.EXPORT:
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