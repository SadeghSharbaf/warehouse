from django.urls import path,include
from inventory.api import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register('receipt', views.ReceiptVS, basename='receipt')

urlpatterns = [
    path('items/',views.ItemListCreateView.as_view(),name='items-list'),
    path('items/<int:pk>/',views.ItemDetailView.as_view(),name='item-detail'),
    
    path('purchase/',views.PurchaseCreateView.as_view(),name='purchase-list-create'),
    path('purchase/<int:pk>/',views.PurchaseDetailView.as_view(),name='purchase-detail'),
    
    path('', include(router.urls)),
    
    path('receipt-item/', views.ReceiptItemView.as_view(),name='receipt-item-list-create'),
    path('receipt-item/<int:pk>/', views.ReceiptItemDetailView.as_view(), name='receipt-item-detail'),
    
    path('summary/',views.StockSummaryView.as_view(),name='summary'),
    path('inventory-history/', views.InventoryHistoryListView.as_view(), name='inventory-history'),
    
    path('returns/', views.ReturnCreateView.as_view(), name='return-list-create'),
    path('returns/<int:pk>/', views.ReturnDetailView.as_view(), name='return-detail'),
    path('returns/history/', views.ReturnHistoryView.as_view(), name='return-detail'),
    
    path('expiring/', views.ExpiringSoonView.as_view(), name='expiring'),
    
    path('audit-trail/', views.AuditLogListView.as_view(), name='audit-trail'),
    
    path('login/', obtain_auth_token, name='login'),
]