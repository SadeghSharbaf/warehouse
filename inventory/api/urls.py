from django.urls import path,include
from inventory.api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('receipt', views.ReceiptVS, basename='receipt')

urlpatterns = [
    path('', include(router.urls)),
    path('items/',views.ItemListCreateView.as_view(),name='items-list'),
    path('items/<int:pk>/',views.ItemDetailView.as_view(),name='item-detail'),
    
    path('purchase/',views.PurchaseCreateView.as_view(),name='purchase-list-create'),
    path('purchase/<int:pk>/',views.PurchaseDetailView.as_view(),name='purchase-detail'),
    
    path('receipt-item/', views.ReceiptItemView.as_view(),name='receipt-item-list-create'),
    path('receipt-item/<int:pk>/', views.ReceiptItemDetailView.as_view(), name='receipt-item-detail'),
    
    path('inventory/',views.InventoryListView.as_view(),name='inventory-list'),
    path('inventory-history/', views.InventoryHistoryListView.as_view(), name='inventory-history'),
    
    path('returns/', views.ReturnCreateView.as_view(), name='return-list-create'),
    path('returns/<int:pk>/', views.ReturnDetailView.as_view(), name='return-detail'),
    path('returns/history/', views.ReceiptHistoryView.as_view(), name='return-history'),
    
    path('expiring/', views.ExpiringSoonView.as_view(), name='expiring')
]
