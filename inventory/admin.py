from django.contrib import admin
from .models import Item,Purchase,Inventory,Receipt,ReceiptItem,Return,AuditLog,InventoryHistory


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'unit']
    search_fields = ['name']
    list_filter = ['unit']
    ordering = ['name']
    
    
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'price_per_unit', 'purchase_date', 'expiration_date']
    search_fields = ['item__name']
    list_filter = ['purchase_date']
    ordering = ['-purchase_date']
    date_hierarchy = 'purchase_date'
    list_editable = ['quantity', 'price_per_unit']
    
    
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['item', 'total_quantity', 'updated_at']
    search_fields = ['item__name']
    readonly_fields = ['updated_at']
    ordering = ['item__name']
    list_per_page = 20
    
    
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'creation_date', 'get_items_count']
    search_fields = ['type', 'optional_notes']
    list_filter = ['type', 'creation_date']
    date_hierarchy = 'creation_date'
    
    def get_items_count(self,obj):
        return obj.receiptitem_set.count()
    get_items_count.short_description = 'quantity of receipt'
    
    
@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ['receipt', 'purchase', 'quantity', 'get_items_name']
    search_fields = ['receipt__type', 'purchase__item__name']
    list_filter = ['receipt__type', 'purchase__item__name']
    
    def get_items_name(self,obj):
        return obj.purchase.item.name
    get_items_name.short_description = 'name of product'
    
    
@admin.register(InventoryHistory)
class InventoryHistoryAdmin(admin.ModelAdmin):
    list_display = ['item', 'receipt', 'change_type', 'quantity_changed', 'timestamp']
    search_fields = ['item__name', 'change_type']
    list_filter = ['change_type', 'timestamp']
    ordering =['timestamp']
    readonly_fields = ['timestamp']
    list_per_page = 20
    
    
@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ['receipt_item', 'quantity_returned', 'return_date', 'get_items_name']
    search_fields = ['receipt_item__purchase__item__name']
    list_filter = ['return_date']
    date_hierarchy = 'return_date'
    list_per_page = 20
    
    def get_items_name(self,obj):
        return obj.receipt_item.purchase.item.name
    get_items_name.short_description = 'product'
    
    
    
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'item', 'quantity', 'timestamp', 'user', 'receipt']
    search_fields = ['user__username', 'item__name']
    list_filter = ['action', 'timestamp']
    date_hierarchy = 'timestamp'