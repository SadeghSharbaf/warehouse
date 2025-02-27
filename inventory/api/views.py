from rest_framework import generics
from inventory.models import Item,Purchase,Inventory
from inventory.api import serializers

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