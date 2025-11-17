from django.contrib import admin
from .models import SparePartCategory, Supplier, SparePartStock, StockMovement, PurchaseOrder, PurchaseOrderItem

@admin.register(SparePartCategory)
class SparePartCategoryAdmin(admin.ModelAdmin):
    list_display = ('id_category', 'name', 'description', 'parent_category', 'created_at')
    list_filter = ('parent_category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id_category', 'created_at', 'updated_at')


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id_supplier', 'name', 'contact_person', 'phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'contact_person', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('id_supplier', 'created_at', 'updated_at')


@admin.register(SparePartStock)
class SparePartStockAdmin(admin.ModelAdmin):
    list_display = ('repuesto', 'category', 'supplier', 'current_stock', 'minimum_stock', 'maximum_stock', 'is_active', 'created_by')
    list_filter = ('is_active', 'category', 'supplier', 'created_at')
    search_fields = ('repuesto__name', 'part_number', 'description', 'created_by__name')
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('id_movement', 'repuesto', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'performed_by', 'performed_at')
    list_filter = ('movement_type', 'performed_at', 'work_order', 'supplier')
    search_fields = ('repuesto__name', 'reason', 'reference_number', 'performed_by__name')
    ordering = ('-performed_at',)
    readonly_fields = ('id_movement', 'performed_at')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id_purchase_order', 'order_number', 'supplier', 'status', 'order_date', 'expected_delivery_date', 'total_amount', 'created_by')
    list_filter = ('status', 'supplier', 'order_date', 'expected_delivery_date')
    search_fields = ('order_number', 'supplier__name', 'notes', 'created_by__name')
    ordering = ('-order_date',)
    readonly_fields = ('id_purchase_order', 'created_at', 'updated_at')


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('id_item', 'purchase_order', 'repuesto', 'quantity_ordered', 'quantity_received', 'unit_price', 'total_price')
    list_filter = ('purchase_order__status', 'repuesto')
    search_fields = ('purchase_order__order_number', 'repuesto__name', 'notes')
    ordering = ('-id_item',)
    readonly_fields = ('id_item',)
