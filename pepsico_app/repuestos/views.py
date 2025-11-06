from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import (
    SparePartCategory, Supplier, SparePartStock, StockMovement,
    PurchaseOrder, PurchaseOrderItem
)
from .forms import (
    SparePartCategoryForm, SupplierForm, SparePartStockForm, StockMovementForm,
    PurchaseOrderForm, PurchaseOrderItemForm, SparePartSearchForm
)
from documents.models import Repuesto


# Dashboard principal de repuestos
@login_required
def repuestos_dashboard(request):
    """Dashboard principal del módulo de repuestos"""
    # Estadísticas generales
    total_repuestos = SparePartStock.objects.filter(is_active=True).count()
    low_stock_count = SparePartStock.objects.filter(
        is_active=True,
        current_stock__lte=F('minimum_stock')
    ).count()
    out_of_stock_count = SparePartStock.objects.filter(
        is_active=True, current_stock=0
    ).count()

    # Movimientos recientes
    recent_movements = StockMovement.objects.select_related('repuesto', 'performed_by')[:10]

    # Alertas de stock bajo
    low_stock_alerts = SparePartStock.objects.filter(
        is_active=True,
        current_stock__lte=F('minimum_stock')
    ).select_related('repuesto')[:5]

    context = {
        'total_repuestos': total_repuestos,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'recent_movements': recent_movements,
        'low_stock_alerts': low_stock_alerts,
    }

    return render(request, 'repuestos/dashboard.html', context)


# Gestión de Categorías
@login_required
def category_list(request):
    """Lista de categorías de repuestos"""
    categories = SparePartCategory.objects.all().order_by('name')
    return render(request, 'repuestos/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        form = SparePartCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('repuestos:category_list')
    else:
        form = SparePartCategoryForm()
    return render(request, 'repuestos/category_form.html', {'form': form, 'title': 'Crear Categoría'})


@login_required
def category_update(request, pk):
    """Editar categoría"""
    category = get_object_or_404(SparePartCategory, pk=pk)
    if request.method == 'POST':
        form = SparePartCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('repuestos:category_list')
    else:
        form = SparePartCategoryForm(instance=category)
    return render(request, 'repuestos/category_form.html', {'form': form, 'title': 'Editar Categoría'})


@login_required
@require_POST
def category_delete(request, pk):
    """Eliminar categoría"""
    category = get_object_or_404(SparePartCategory, pk=pk)
    try:
        category.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar la categoría: {str(e)}')
    return redirect('repuestos:category_list')


# Gestión de Proveedores
@login_required
def supplier_list(request):
    """Lista de proveedores"""
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'repuestos/supplier_list.html', {'suppliers': suppliers})


@login_required
def supplier_create(request):
    """Crear nuevo proveedor"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente.')
            return redirect('repuestos:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'repuestos/supplier_form.html', {'form': form, 'title': 'Crear Proveedor'})


@login_required
def supplier_update(request, pk):
    """Editar proveedor"""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente.')
            return redirect('repuestos:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'repuestos/supplier_form.html', {'form': form, 'title': 'Editar Proveedor'})


@login_required
def supplier_detail(request, pk):
    """Ver detalles de proveedor"""
    supplier = get_object_or_404(Supplier, pk=pk)
    # Obtener órdenes de compra relacionadas
    purchase_orders = PurchaseOrder.objects.filter(supplier=supplier).order_by('-created_at')[:10]
    return render(request, 'repuestos/supplier_detail.html', {
        'supplier': supplier,
        'purchase_orders': purchase_orders
    })


@login_required
@require_POST
def supplier_delete(request, pk):
    """Eliminar proveedor"""
    supplier = get_object_or_404(Supplier, pk=pk)
    try:
        supplier.delete()
        messages.success(request, 'Proveedor eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el proveedor: {str(e)}')
    return redirect('repuestos:supplier_list')


# Gestión de Repuestos y Stock
@login_required
def spare_part_list(request):
    """Lista de repuestos con filtros de búsqueda"""
    # Procesar formulario de búsqueda
    search_form = SparePartSearchForm(request.GET)
    spare_parts = SparePartStock.objects.select_related('repuesto', 'category', 'supplier').filter(is_active=True)

    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        category = search_form.cleaned_data.get('category')
        supplier = search_form.cleaned_data.get('supplier')
        stock_status = search_form.cleaned_data.get('stock_status')

        if search:
            spare_parts = spare_parts.filter(
                Q(repuesto__name__icontains=search) |
                Q(part_number__icontains=search) |
                Q(description__icontains=search)
            )

        if category:
            spare_parts = spare_parts.filter(category=category)

        if supplier:
            spare_parts = spare_parts.filter(supplier=supplier)

        if stock_status:
            if stock_status == 'low':
                spare_parts = spare_parts.filter(current_stock__lte=F('minimum_stock'))
            elif stock_status == 'out':
                spare_parts = spare_parts.filter(current_stock=0)
            elif stock_status == 'over':
                spare_parts = spare_parts.filter(current_stock__gt=F('maximum_stock'))

    # Paginación
    paginator = Paginator(spare_parts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }

    return render(request, 'repuestos/spare_part_list.html', context)


@login_required
def spare_part_detail(request, pk):
    """Detalle de un repuesto"""
    stock_info = get_object_or_404(SparePartStock.objects.select_related(
        'repuesto', 'category', 'supplier', 'created_by'
    ), pk=pk)

    # Movimientos recientes
    recent_movements = StockMovement.objects.filter(
        repuesto=stock_info.repuesto
    ).select_related('performed_by', 'work_order').order_by('-performed_at')[:10]

    # Uso en órdenes de trabajo recientes
    from documents.models import SparePartUsage
    recent_usage = SparePartUsage.objects.filter(
        repuesto=stock_info.repuesto
    ).select_related('work_order').order_by('-used_datetime')[:5]

    context = {
        'stock_info': stock_info,
        'recent_movements': recent_movements,
        'recent_usage': recent_usage,
    }

    return render(request, 'repuestos/spare_part_detail.html', context)


@login_required
def spare_part_create(request):
    """Crear nuevo repuesto con información de stock"""
    if request.method == 'POST':
        form = SparePartStockForm(request.POST)
        if form.is_valid():
            # Crear el repuesto primero si no existe
            repuesto_data = {
                'name': form.cleaned_data['repuesto'].name if hasattr(form.cleaned_data['repuesto'], 'name') else str(form.cleaned_data['repuesto']),
                'quantity': form.cleaned_data['current_stock'],
            }

            # Si es un repuesto existente, actualizarlo
            if isinstance(form.cleaned_data['repuesto'], Repuesto):
                repuesto = form.cleaned_data['repuesto']
                repuesto.quantity = form.cleaned_data['current_stock']
                repuesto.save()
            else:
                # Crear nuevo repuesto
                repuesto = Repuesto.objects.create(**repuesto_data)

            # Crear información de stock
            stock_info = form.save(commit=False)
            stock_info.repuesto = repuesto
            stock_info.created_by = request.user.flotauser if hasattr(request.user, 'flotauser') else None
            stock_info.save()

            # Crear movimiento inicial de entrada
            StockMovement.objects.create(
                repuesto=repuesto,
                movement_type='IN',
                quantity=form.cleaned_data['current_stock'],
                previous_stock=0,
                new_stock=form.cleaned_data['current_stock'],
                reason='Creación inicial de stock',
                performed_by=request.user.flotauser if hasattr(request.user, 'flotauser') else None
            )

            messages.success(request, 'Repuesto creado exitosamente.')
            return redirect('repuestos:spare_part_list')
    else:
        form = SparePartStockForm()

    return render(request, 'repuestos/spare_part_form.html', {'form': form, 'title': 'Crear Repuesto'})


@login_required
def spare_part_update(request, pk):
    """Editar repuesto"""
    stock_info = get_object_or_404(SparePartStock, pk=pk)
    if request.method == 'POST':
        form = SparePartStockForm(request.POST, instance=stock_info)
        if form.is_valid():
            # Actualizar cantidad en el modelo Repuesto
            repuesto = stock_info.repuesto
            repuesto.quantity = form.cleaned_data['current_stock']
            repuesto.save()

            form.save()
            messages.success(request, 'Repuesto actualizado exitosamente.')
            return redirect('repuestos:spare_part_detail', pk=pk)
    else:
        form = SparePartStockForm(instance=stock_info)

    return render(request, 'repuestos/spare_part_form.html', {'form': form, 'title': 'Editar Repuesto'})


@login_required
@require_POST
def spare_part_delete(request, pk):
    """Eliminar repuesto"""
    stock_info = get_object_or_404(SparePartStock, pk=pk)
    try:
        # Marcar como inactivo en lugar de eliminar
        stock_info.is_active = False
        stock_info.save()
        messages.success(request, 'Repuesto marcado como inactivo.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el repuesto: {str(e)}')
    return redirect('repuestos:spare_part_list')


# Gestión de Movimientos de Stock
@login_required
def stock_movement_list(request):
    """Lista de movimientos de stock"""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    movements = StockMovement.objects.select_related(
        'repuesto', 'performed_by', 'work_order', 'supplier'
    ).order_by('-performed_at')

    # Calcular estadísticas
    total_movements = movements.count()
    total_entries = movements.filter(movement_type='IN').count()
    total_exits = movements.filter(movement_type='OUT').count()
    
    # Movimientos de esta semana (últimos 7 días)
    week_ago = timezone.now() - timedelta(days=7)
    this_week_movements = movements.filter(performed_at__gte=week_ago).count()

    # Filtros
    repuesto_filter = request.GET.get('repuesto')
    type_filter = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    user_filter = request.GET.get('created_by')

    if repuesto_filter:
        movements = movements.filter(repuesto__name__icontains=repuesto_filter)
    if type_filter:
        movements = movements.filter(movement_type=type_filter)
    if date_from:
        movements = movements.filter(performed_at__date__gte=date_from)
    if date_to:
        movements = movements.filter(performed_at__date__lte=date_to)
    if user_filter:
        movements = movements.filter(performed_by__pk=user_filter)

    # Lista de usuarios para el filtro
    from documents.models import FlotaUser
    users = FlotaUser.objects.all().order_by('name')

    paginator = Paginator(movements, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'users': users,
        'total_movements': total_movements,
        'total_entries': total_entries,
        'total_exits': total_exits,
        'this_week_movements': this_week_movements,
    }

    return render(request, 'repuestos/stock_movement_list.html', context)


@login_required
def stock_movement_detail(request, pk):
    """Detalle de movimiento de stock"""
    movement = get_object_or_404(
        StockMovement.objects.select_related(
            'repuesto', 'performed_by', 'work_order', 'purchase_order', 'supplier'
        ),
        pk=pk
    )

    # Obtener información del stock del repuesto
    try:
        spare_part_stock = SparePartStock.objects.select_related('repuesto', 'category').get(repuesto=movement.repuesto)
    except SparePartStock.DoesNotExist:
        spare_part_stock = None

    context = {
        'movement': movement,
        'spare_part_stock': spare_part_stock,
    }

    return render(request, 'repuestos/stock_movement_detail.html', context)


@login_required
def stock_movement_create(request):
    """Crear movimiento de stock"""
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)

            # Obtener stock actual
            stock_info = SparePartStock.objects.filter(repuesto=movement.repuesto).first()
            if not stock_info:
                messages.error(request, 'No se encontró información de stock para este repuesto.')
                return redirect('repuestos:stock_movement_create')

            movement.previous_stock = stock_info.current_stock

            # Calcular nuevo stock según tipo de movimiento
            if movement.movement_type == 'IN':
                movement.new_stock = movement.previous_stock + movement.quantity
            elif movement.movement_type == 'OUT':
                if movement.previous_stock < movement.quantity:
                    messages.error(request, 'Stock insuficiente para esta salida.')
                    return redirect('repuestos:stock_movement_create')
                movement.new_stock = movement.previous_stock - movement.quantity
            elif movement.movement_type == 'ADJ':
                movement.new_stock = movement.quantity  # El quantity aquí es el stock final deseado
            elif movement.movement_type == 'RET':
                movement.new_stock = movement.previous_stock + movement.quantity

            movement.performed_by = request.user.flotauser if hasattr(request.user, 'flotauser') else None
            movement.save()

            messages.success(request, 'Movimiento de stock registrado exitosamente.')
            return redirect('repuestos:stock_movement_list')
    else:
        form = StockMovementForm()

    return render(request, 'repuestos/stock_movement_form.html', {'form': form, 'title': 'Registrar Movimiento'})


# Gestión de Órdenes de Compra
@login_required
def purchase_order_list(request):
    """Lista de órdenes de compra"""
    orders = PurchaseOrder.objects.select_related('supplier', 'created_by').order_by('-created_at')

    # Filtros
    supplier_filter = request.GET.get('supplier')
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    user_filter = request.GET.get('created_by')

    if supplier_filter:
        orders = orders.filter(supplier__pk=supplier_filter)
    if status_filter:
        orders = orders.filter(status=status_filter)
    if date_from:
        orders = orders.filter(order_date__gte=date_from)
    if date_to:
        orders = orders.filter(order_date__lte=date_to)
    if user_filter:
        orders = orders.filter(created_by__pk=user_filter)

    # Estadísticas de órdenes por estado (sin aplicar filtros)
    all_orders = PurchaseOrder.objects.all()
    draft_count = all_orders.filter(status='DRAFT').count()
    sent_count = all_orders.filter(status__in=['PENDING', 'APPROVED', 'ORDERED']).count()
    completed_count = all_orders.filter(status='RECEIVED').count()
    total_orders = all_orders.count()

    # Paginación
    paginator = Paginator(orders, 25)  # 25 órdenes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Datos para los filtros
    suppliers = Supplier.objects.all().order_by('name')
    from documents.models import FlotaUser
    users = FlotaUser.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'suppliers': suppliers,
        'users': users,
        'draft_count': draft_count,
        'sent_count': sent_count,
        'completed_count': completed_count,
        'total_orders': total_orders,
    }

    return render(request, 'repuestos/purchase_order_list.html', context)


@login_required
def purchase_order_create(request):
    """Crear orden de compra"""
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user.flotauser if hasattr(request.user, 'flotauser') else None
            
            # Generar número de orden único
            from datetime import datetime
            year = datetime.now().year
            month = datetime.now().month
            base_number = f"{year}{month:02d}"
            
            # Encontrar el siguiente número disponible
            counter = 1
            while True:
                order_number = f"{base_number}{counter:03d}"
                if not PurchaseOrder.objects.filter(order_number=order_number).exists():
                    break
                counter += 1
            
            order.order_number = order_number
            
            # Establecer fecha de orden
            order.order_date = datetime.now().date()
            
            order.save()

            # Procesar items
            items_data = []
            for key, value in request.POST.items():
                if key.startswith('items[') and key.endswith('][spare_part]'):
                    # Extraer el índice del item
                    index = key.split('[')[1].split(']')[0]
                    items_data.append({
                        'index': index,
                        'spare_part': value,
                        'quantity': request.POST.get(f'items[{index}][quantity]', 0),
                        'unit_price': request.POST.get(f'items[{index}][unit_price]', 0),
                    })

            # Crear items de la orden
            subtotal = 0
            for item_data in items_data:
                if item_data['spare_part'] and int(item_data['quantity']) > 0:
                    unit_price = float(item_data['unit_price']) if item_data['unit_price'] else 0
                    quantity = int(item_data['quantity'])
                    subtotal += unit_price * quantity
                    
                    PurchaseOrderItem.objects.create(
                        purchase_order=order,
                        repuesto_id=item_data['spare_part'],
                        quantity_ordered=quantity,
                        unit_price=unit_price,
                        total_price=unit_price * quantity,
                    )

            # Calcular totales
            order.subtotal = subtotal
            order.tax_amount = subtotal * 0.19  # Asumiendo 19% de IVA
            order.total_amount = order.subtotal + order.tax_amount
            order.save()

            messages.success(request, 'Orden de compra creada exitosamente.')
            return redirect('repuestos:purchase_order_detail', pk=order.pk)
        else:
            print("Form errors:", form.errors)  # Debug
    else:
        form = PurchaseOrderForm()

    # Obtener lista de repuestos para el select
    spare_parts = SparePartStock.objects.select_related('repuesto').filter(is_active=True).order_by('repuesto__name')

    context = {
        'form': form,
        'spare_parts': spare_parts,
        'title': 'Crear Orden de Compra'
    }

    return render(request, 'repuestos/purchase_order_form.html', context)


@login_required
def purchase_order_update(request, pk):
    """Editar información básica de orden de compra (proveedor, fechas, notas)"""
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Solo permitir editar órdenes en estado DRAFT
    if order.status != 'DRAFT':
        messages.error(request, 'Solo se pueden editar órdenes en estado Borrador.')
        return redirect('repuestos:purchase_order_detail', pk=pk)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Información básica de la orden de compra actualizada exitosamente.')
            return redirect('repuestos:purchase_order_detail', pk=pk)
    else:
        form = PurchaseOrderForm(instance=order)

    # Obtener lista de repuestos para el select (aunque no se editan items aquí)
    spare_parts = SparePartStock.objects.select_related('repuesto').filter(is_active=True).order_by('repuesto__name')

    context = {
        'form': form,
        'spare_parts': spare_parts,
        'title': 'Editar Información Básica de Orden de Compra' if order else 'Crear Orden de Compra'
    }

    return render(request, 'repuestos/purchase_order_form.html', context)


@login_required
def purchase_order_detail(request, pk):
    """Detalle de orden de compra"""
    order = get_object_or_404(
        PurchaseOrder.objects.select_related('supplier', 'created_by', 'approved_by'),
        pk=pk
    )
    items = order.items.select_related('repuesto').all()

    context = {
        'order': order,
        'items': items,
    }

    return render(request, 'repuestos/purchase_order_detail.html', context)


@login_required
@require_POST
def purchase_order_change_status(request, pk):
    """Cambiar estado de orden de compra"""
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    new_status = request.POST.get('new_status')
    notes = request.POST.get('notes', '')
    
    if new_status not in dict(PurchaseOrder.STATUS_CHOICES):
        messages.error(request, 'Estado no válido.')
        return redirect('repuestos:purchase_order_detail', pk=pk)
    
    # Validar transiciones de estado
    valid_transitions = {
        'DRAFT': ['PENDING', 'CANCELLED'],
        'PENDING': ['APPROVED', 'RECEIVED', 'CANCELLED'],
        'APPROVED': ['ORDERED', 'RECEIVED', 'CANCELLED'],
        'ORDERED': ['RECEIVED', 'CANCELLED'],
        'RECEIVED': [],
        'CANCELLED': []
    }
    
    if new_status not in valid_transitions.get(order.status, []):
        messages.error(request, f'No se puede cambiar el estado de {order.get_status_display()} a {dict(PurchaseOrder.STATUS_CHOICES)[new_status]}.')
        return redirect('repuestos:purchase_order_detail', pk=pk)
    
    old_status = order.status
    order.status = new_status
    
    # Actualizar campos de fecha según el estado
    from datetime import datetime
    if new_status == 'ORDERED':
        order.actual_delivery_date = datetime.now().date()
    elif new_status == 'RECEIVED':
        order.actual_delivery_date = datetime.now().date()
    
    order.save()
    
    # Agregar notas si se proporcionaron
    if notes:
        order.notes = (order.notes or '') + f'\n[{datetime.now()}] Estado cambiado de {old_status} a {new_status}: {notes}'
        order.save()
    
    messages.success(request, f'Estado de la orden cambiado a {order.get_status_display()}.')
    return redirect('repuestos:purchase_order_detail', pk=pk)


@login_required
def purchase_order_update_stock_status(request, pk):
    """Actualizar estado de actualización manual de stock"""
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        stock_updated = request.POST.get('stock_updated') == 'true'
        
        order.stock_updated_manually = stock_updated
        if stock_updated:
            order.stock_updated_by = request.user.flotauser if hasattr(request.user, 'flotauser') else None
            from datetime import datetime
            order.stock_updated_at = datetime.now()
        else:
            order.stock_updated_by = None
            order.stock_updated_at = None
        
        order.save()
        
        status_text = "marcado como actualizado" if stock_updated else "desmarcado como actualizado"
        messages.success(request, f'Stock de la orden {status_text} manualmente.')
    
    return redirect('repuestos:purchase_order_detail', pk=pk)


# API endpoints para AJAX
@login_required
def get_spare_part_stock(request, repuesto_id):
    """API para obtener stock actual de un repuesto"""
    try:
        stock_info = SparePartStock.objects.get(repuesto=repuesto_id)
        data = {
            'current_stock': stock_info.current_stock,
            'minimum_stock': stock_info.minimum_stock,
            'unit_cost': float(stock_info.unit_cost),
        }
        return JsonResponse(data)
    except SparePartStock.DoesNotExist:
        return JsonResponse({'error': 'Repuesto no encontrado'}, status=404)
