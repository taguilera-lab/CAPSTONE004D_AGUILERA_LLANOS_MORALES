from django import forms
from .models import (
    SparePartCategory, Supplier, SparePartStock, StockMovement,
    PurchaseOrder, PurchaseOrderItem
)
from documents.models import Repuesto


class SparePartCategoryForm(forms.ModelForm):
    """Formulario para categorías de repuestos"""
    class Meta:
        model = SparePartCategory
        fields = ['name', 'description', 'parent_category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'parent_category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class SupplierForm(forms.ModelForm):
    """Formulario para proveedores"""
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proveedor'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Persona de contacto'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class SparePartStockForm(forms.ModelForm):
    """Formulario para gestión de stock de repuestos"""
    class Meta:
        model = SparePartStock
        fields = [
            'repuesto', 'category', 'supplier', 'part_number', 'description',
            'unit_cost', 'selling_price', 'current_stock', 'minimum_stock',
            'maximum_stock', 'location', 'is_active', 'requires_approval'
        ]
        widgets = {
            'repuesto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'part_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de parte'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'current_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'minimum_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'maximum_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación física'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_approval': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class StockMovementForm(forms.ModelForm):
    """Formulario para movimientos de stock"""
    class Meta:
        model = StockMovement
        fields = [
            'repuesto', 'movement_type', 'quantity', 'work_order',
            'purchase_order', 'supplier', 'reason', 'reference_number'
        ]
        widgets = {
            'repuesto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'movement_type': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'work_order': forms.Select(attrs={
                'class': 'form-select'
            }),
            'purchase_order': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_purchase_order'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivo del movimiento'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de referencia (factura, OC, etc.)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo work orders activas
        from documents.models import WorkOrder, WorkOrderStatus
        try:
            completed_status = WorkOrderStatus.objects.get(name='Completada')
            self.fields['work_order'].queryset = WorkOrder.objects.exclude(status=completed_status)
        except WorkOrderStatus.DoesNotExist:
            pass
        
        # Filtrar órdenes de compra que no estén completadas
        self.fields['purchase_order'].queryset = PurchaseOrder.objects.exclude(status='RECEIVED')


class PurchaseOrderForm(forms.ModelForm):
    """Formulario para órdenes de compra"""
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier', 'expected_delivery_date', 'notes'
        ]
        widgets = {
            'order_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de orden de compra'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'order_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expected_delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            }),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    """Formulario para items de orden de compra"""
    class Meta:
        model = PurchaseOrderItem
        fields = ['repuesto', 'quantity_ordered', 'unit_price', 'notes']
        widgets = {
            'repuesto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity_ordered': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas del item'
            }),
        }


# Formulario para búsqueda y filtros
class SparePartSearchForm(forms.Form):
    """Formulario de búsqueda de repuestos"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, número de parte...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=SparePartCategory.objects.all(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        empty_label="Todos los proveedores",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    stock_status = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('low', 'Stock Bajo'),
            ('normal', 'Stock Normal'),
            ('over', 'Sobre Stock'),
            ('out', 'Sin Stock'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )