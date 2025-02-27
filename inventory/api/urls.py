from django.urls import path,include
from inventory.api import views


urlpatterns = [
    path('items/',views.ItemListCreateView.as_view(),name='items-list'),
    path('items/<int:pk>/',views.ItemDetailView.as_view(),name='item-detail'),
    
    path('purchase/',views.PurchaseCreateView.as_view(),name='purchase-list-create'),
    path('purchase/<int:pk>/',views.PurchaseDetailView.as_view(),name='purchase-detail'),
    
    path('inventory/',views.InventoryListView.as_view(),name='inventory-list'),
]
