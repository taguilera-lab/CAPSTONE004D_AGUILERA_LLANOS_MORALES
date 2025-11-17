from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from documents.models import Repuesto, Site, FlotaUser


class SparePartCategory(models.Model):
    """Categorías para clasificar repuestos"""
    id_category = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    parent_category = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subcategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'SparePartCategories'
        verbose_name = 'Categoría de Repuesto'
        verbose_name_plural = 'Categorías de Repuestos'


class Supplier(models.Model):
    """Proveedores de repuestos"""
    id_supplier = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Suppliers'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'


class SparePartStock(models.Model):
    """Stock e inventario de repuestos"""
    repuesto = models.OneToOneField(
        Repuesto, on_delete=models.CASCADE, related_name='stock_info'
    )
    category = models.ForeignKey(
        SparePartCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Información del repuesto
    part_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Gestión de stock
    current_stock = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=0)
    maximum_stock = models.IntegerField(default=0)
    location = models.CharField(max_length=100, null=True, blank=True)

    # Control de calidad
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)

    # Metadata
    created_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_spare_parts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.repuesto.name} - Stock: {self.current_stock}"

    def is_low_stock(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.current_stock <= self.minimum_stock

    def is_overstock(self):
        """Verifica si el stock está por encima del máximo"""
        return self.current_stock > self.maximum_stock

    class Meta:
        db_table = 'SparePartStocks'
        verbose_name = 'Stock de Repuesto'
        verbose_name_plural = 'Stocks de Repuestos'


class StockMovement(models.Model):
    """Movimientos de stock (entradas, salidas, ajustes)"""
    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
        ('ADJ', 'Ajuste'),
        ('RET', 'Devolución'),
    ]

    id_movement = models.AutoField(primary_key=True)
    repuesto = models.ForeignKey(
        Repuesto, on_delete=models.CASCADE, related_name='movements'
    )
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()

    # Referencias opcionales
    work_order = models.ForeignKey(
        'documents.WorkOrder', on_delete=models.SET_NULL, null=True, blank=True
    )
    purchase_order = models.ForeignKey(
        'PurchaseOrder', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_movements'
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Información adicional
    reason = models.TextField(null=True, blank=True)
    reference_number = models.CharField(max_length=50, null=True, blank=True)  # Factura, orden de compra, etc.

    # Usuario que realizó el movimiento
    performed_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    performed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.repuesto.name} - {self.get_movement_type_display()} ({self.quantity})"

    class Meta:
        db_table = 'StockMovements'
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-performed_at']


class PurchaseOrder(models.Model):
    """Órdenes de compra de repuestos"""
    STATUS_CHOICES = [
        ('DRAFT', 'Borrador'),
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobada'),
        ('ORDERED', 'Ordenada'),
        ('RECEIVED', 'Recibida'),
        ('CANCELLED', 'Cancelada'),
    ]

    id_purchase_order = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')

    # Fechas
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)

    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Información adicional
    notes = models.TextField(null=True, blank=True)
    stock_updated_manually = models.BooleanField(default=False)
    stock_updated_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_updated_purchase_orders'
    )
    stock_updated_at = models.DateTimeField(null=True, blank=True)

    # Usuarios
    created_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_purchase_orders'
    )
    approved_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_purchase_orders'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OC-{self.order_number} - {self.supplier.name}"

    class Meta:
        db_table = 'PurchaseOrders'
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'


class PurchaseOrderItem(models.Model):
    """Items de una orden de compra"""
    id_item = models.AutoField(primary_key=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='items'
    )
    repuesto = models.ForeignKey(Repuesto, on_delete=models.CASCADE)
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Información adicional
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.purchase_order} - {self.repuesto.name}"

    def is_fully_received(self):
        return self.quantity_received >= self.quantity_ordered

    class Meta:
        db_table = 'PurchaseOrderItems'
        verbose_name = 'Item de Orden de Compra'
        verbose_name_plural = 'Items de Órdenes de Compra'


# Señales para actualizar stock automáticamente
@receiver(post_save, sender=StockMovement)
def update_stock_on_movement(sender, instance, created, **kwargs):
    """Actualiza el stock del repuesto cuando hay un movimiento"""
    if created:
        stock_info = SparePartStock.objects.filter(repuesto=instance.repuesto).first()
        if stock_info:
            stock_info.current_stock = instance.new_stock
            stock_info.save(update_fields=['current_stock', 'updated_at'])
