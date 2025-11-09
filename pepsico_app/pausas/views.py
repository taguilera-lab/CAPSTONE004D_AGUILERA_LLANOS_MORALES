from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import WorkOrderPause, PauseType
from .forms import WorkOrderPauseForm, PauseTypeForm, QuickPauseForm
from documents.models import WorkOrder, WorkOrderMechanic, Repuesto


# Dashboard de Pausas
@login_required
def pauses_dashboard(request):
    """Dashboard principal del módulo de pausas"""
    # Estadísticas generales
    total_pauses = WorkOrderPause.objects.filter(is_active=True).count()
    active_pauses = WorkOrderPause.objects.filter(
        is_active=True,
        end_datetime__isnull=True
    ).count()
    completed_today = WorkOrderPause.objects.filter(
        is_active=True,
        end_datetime__isnull=False,
        end_datetime__date=timezone.now().date()
    ).count()

    # Pausas por tipo
    pauses_by_type = WorkOrderPause.objects.filter(is_active=True).values(
        'pause_type__name'
    ).annotate(count=Count('id_pause')).order_by('-count')[:5]

    # Pausas activas recientes
    recent_active_pauses = WorkOrderPause.objects.filter(
        is_active=True,
        end_datetime__isnull=True
    ).select_related(
        'work_order', 'mechanic_assignment__mechanic', 'pause_type'
    ).order_by('-start_datetime')[:10]

    # Órdenes de trabajo con más pausas
    work_orders_with_pauses = WorkOrder.objects.annotate(
        pause_count=Count('pauses')
    ).filter(pause_count__gt=0).order_by('-pause_count')[:5]

    context = {
        'total_pauses': total_pauses,
        'active_pauses': active_pauses,
        'completed_today': completed_today,
        'pauses_by_type': pauses_by_type,
        'recent_active_pauses': recent_active_pauses,
        'work_orders_with_pauses': work_orders_with_pauses,
    }

    return render(request, 'pausas/dashboard.html', context)


# Gestión de Tipos de Pausa
@login_required
def pause_type_list(request):
    """Lista de tipos de pausa"""
    pause_types = PauseType.objects.all().order_by('name')
    
    # Estadísticas
    total_types = pause_types.count()
    active_types = pause_types.filter(is_active=True).count()
    inactive_types = pause_types.filter(is_active=False).count()
    
    context = {
        'pause_types': pause_types,
        'total_types': total_types,
        'active_types': active_types,
        'inactive_types': inactive_types,
    }
    
    return render(request, 'pausas/pause_type_list.html', context)


@login_required
def pause_type_create(request):
    """Crear nuevo tipo de pausa"""
    if request.method == 'POST':
        form = PauseTypeForm(request.POST)
        if form.is_valid():
            pause_type = form.save(commit=False)
            pause_type.created_by = request.user.flotauser
            pause_type.save()
            messages.success(request, 'Tipo de pausa creado exitosamente.')
            return redirect('pausas:pause_type_list')
    else:
        form = PauseTypeForm()

    return render(request, 'pausas/pause_type_form.html', {
        'form': form,
        'title': 'Crear Tipo de Pausa'
    })


@login_required
def pause_type_update(request, pk):
    """Editar tipo de pausa"""
    pause_type = get_object_or_404(PauseType, pk=pk)
    if request.method == 'POST':
        form = PauseTypeForm(request.POST, instance=pause_type)
        if form.is_valid():
            pause_type = form.save(commit=False)
            pause_type.updated_by = request.user.flotauser
            pause_type.save()
            messages.success(request, 'Tipo de pausa actualizado exitosamente.')
            return redirect('pausas:pause_type_list')
    else:
        form = PauseTypeForm(instance=pause_type)

    return render(request, 'pausas/pause_type_form.html', {
        'form': form,
        'title': 'Editar Tipo de Pausa'
    })


@login_required
def pause_type_detail(request, pk):
    """Detalle de tipo de pausa"""
    pause_type = get_object_or_404(PauseType, pk=pk)
    
    # Estadísticas del tipo
    total_pauses = WorkOrderPause.objects.filter(pause_type=pause_type, is_active=True).count()
    active_pauses = WorkOrderPause.objects.filter(
        pause_type=pause_type, is_active=True, end_datetime__isnull=True
    ).count()
    completed_pauses = total_pauses - active_pauses
    
    # Pausas recientes
    recent_pauses = WorkOrderPause.objects.filter(
        pause_type=pause_type, is_active=True
    ).select_related('work_order', 'mechanic_assignment__mechanic').order_by('-start_datetime')[:10]
    
    # Última pausa
    last_pause = WorkOrderPause.objects.filter(
        pause_type=pause_type, is_active=True
    ).order_by('-start_datetime').first()
    
    context = {
        'pause_type': pause_type,
        'total_pauses': total_pauses,
        'active_pauses': active_pauses,
        'completed_pauses': completed_pauses,
        'recent_pauses': recent_pauses,
        'last_pause': last_pause,
    }
    
    return render(request, 'pausas/pause_type_detail.html', context)


@login_required
def pause_type_deactivate(request, pk):
    """Desactivar tipo de pausa"""
    pause_type = get_object_or_404(PauseType, pk=pk)
    
    if request.method == 'POST' and 'confirm' in request.POST:
        pause_type.is_active = False
        pause_type.updated_by = request.user.flotauser
        pause_type.save()
        messages.success(request, f'Tipo de pausa "{pause_type.name}" desactivado exitosamente.')
        return redirect('pausas:pause_type_list')
    
    return render(request, 'pausas/pause_type_toggle_status.html', {
        'pause_type': pause_type,
        'action': 'desactivar'
    })


@login_required
def pause_type_activate(request, pk):
    """Activar tipo de pausa"""
    pause_type = get_object_or_404(PauseType, pk=pk)
    
    if request.method == 'POST' and 'confirm' in request.POST:
        pause_type.is_active = True
        pause_type.updated_by = request.user.flotauser
        pause_type.save()
        messages.success(request, f'Tipo de pausa "{pause_type.name}" activado exitosamente.')
        return redirect('pausas:pause_type_list')
    
    return render(request, 'pausas/pause_type_toggle_status.html', {
        'pause_type': pause_type,
        'action': 'activar'
    })


# Gestión de Pausas en Órdenes de Trabajo
@login_required
def work_order_pause_list(request):
    """Lista de pausas en órdenes de trabajo"""
    pauses = WorkOrderPause.objects.select_related(
        'work_order', 'mechanic_assignment__mechanic', 'pause_type',
        'created_by', 'affected_spare_part'
    ).filter(is_active=True).order_by('-start_datetime')

    # Filtros
    work_order_filter = request.GET.get('work_order')
    pause_type_filter = request.GET.get('pause_type')
    status_filter = request.GET.get('status')  # active/completed
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if work_order_filter:
        pauses = pauses.filter(work_order__id_work_order=work_order_filter)
    if pause_type_filter:
        pauses = pauses.filter(pause_type__id_pause_type=pause_type_filter)
    if status_filter == 'active':
        pauses = pauses.filter(end_datetime__isnull=True)
    elif status_filter == 'completed':
        pauses = pauses.filter(end_datetime__isnull=False)
    if date_from:
        pauses = pauses.filter(start_datetime__date__gte=date_from)
    if date_to:
        pauses = pauses.filter(start_datetime__date__lte=date_to)

    # Estadísticas
    total_pauses = pauses.count()
    active_pauses = pauses.filter(end_datetime__isnull=True).count()
    completed_pauses = pauses.filter(end_datetime__isnull=False).count()

    context = {
        'pauses': pauses,
        'total_pauses': total_pauses,
        'active_pauses': active_pauses,
        'completed_pauses': completed_pauses,
        'pause_types': PauseType.objects.filter(is_active=True),
    }

    return render(request, 'pausas/work_order_pause_list.html', context)


@login_required
def work_order_pause_create(request):
    """Crear nueva pausa en orden de trabajo"""
    if request.method == 'POST':
        form = WorkOrderPauseForm(request.POST)
        if form.is_valid():
            pause = form.save(commit=False)
            pause.created_by = request.user.flotauser if hasattr(request.user, 'flotauser') else None
            pause.save()
            messages.success(request, 'Pausa registrada exitosamente.')
            return redirect('pausas:work_order_pause_list')
    else:
        form = WorkOrderPauseForm()

    return render(request, 'pausas/work_order_pause_form.html', {
        'form': form,
        'title': 'Registrar Nueva Pausa'
    })


@login_required
def work_order_pause_detail(request, pk):
    """Detalle de una pausa"""
    pause = get_object_or_404(
        WorkOrderPause.objects.select_related(
            'work_order', 'mechanic_assignment__mechanic', 'pause_type',
            'created_by', 'authorized_by', 'affected_spare_part'
        ),
        pk=pk
    )

    return render(request, 'pausas/work_order_pause_detail.html', {'pause': pause})


@login_required
def work_order_pause_end(request, pk):
    """Finalizar una pausa activa"""
    pause = get_object_or_404(WorkOrderPause, pk=pk, is_active=True, end_datetime__isnull=True)

    if request.method == 'POST':
        pause.end_datetime = timezone.now()
        pause.save()
        messages.success(request, f'Pausa finalizada. Duración: {pause.duration_display}')
        return redirect('pausas:work_order_pause_detail', pk=pause.pk)

    return render(request, 'pausas/work_order_pause_end.html', {'pause': pause})


@login_required
def work_order_pause_authorize(request, pk):
    """Autorizar una pausa que requiere autorización"""
    pause = get_object_or_404(WorkOrderPause, pk=pk, requires_authorization=True, authorized_by__isnull=True)

    if request.method == 'POST':
        pause.authorized_by = request.user.flotauser if hasattr(request.user, 'flotauser') else None
        pause.authorized_at = timezone.now()
        pause.save()
        messages.success(request, 'Pausa autorizada exitosamente.')
        return redirect('pausas:work_order_pause_detail', pk=pause.pk)

    return render(request, 'pausas/work_order_pause_authorize.html', {'pause': pause})


# Pausas Rápidas
@login_required
def quick_pause_create(request):
    """Crear pausa rápida para casos comunes"""
    if request.method == 'POST':
        form = QuickPauseForm(request.POST)
        if form.is_valid():
            work_order = form.clean_work_order_id()
            pause_type = form.cleaned_data['pause_type']
            
            # Si es pausa por falta de repuestos (STOCK), afecta a todos los mecánicos
            if pause_type.id_pause_type == 'STOCK':
                # Verificar si ya hay una pausa por stock activa
                existing_stock_pause = WorkOrderPause.objects.filter(
                    work_order=work_order,
                    pause_type=pause_type,
                    is_active=True,
                    end_datetime__isnull=True
                ).first()
                
                if existing_stock_pause:
                    messages.warning(request, 'Ya existe una pausa por falta de repuestos activa para esta orden de trabajo.')
                    return redirect('pausas:work_order_pause_list')
                
                # Crear una pausa global que afecta a todos los mecánicos
                pause = WorkOrderPause(
                    work_order=work_order,
                    mechanic_assignment=None,  # Pausa global
                    pause_type=pause_type,
                    reason=form.cleaned_data['reason'],
                    start_datetime=timezone.now(),
                    affected_spare_part=form.clean_spare_part_id(),
                    required_quantity=form.cleaned_data.get('required_quantity'),
                    created_by=request.user.flotauser if hasattr(request.user, 'flotauser') else None
                )

                # Si es pausa por stock, obtener cantidad disponible
                if pause.affected_spare_part:
                    try:
                        from repuestos.models import SparePartStock
                        stock_info = SparePartStock.objects.get(repuesto=pause.affected_spare_part)
                        pause.available_quantity = stock_info.current_stock
                    except:
                        pass

                pause.save()
                messages.success(request, 'Pausa por falta de repuestos registrada. Todos los mecánicos están pausados.')
                    
            else:
                # Para otros tipos de pausa, crear pausa normal (individual)
                pause = WorkOrderPause(
                    work_order=work_order,
                    mechanic_assignment=form.clean_mechanic_id(),
                    pause_type=pause_type,
                    reason=form.cleaned_data['reason'],
                    start_datetime=timezone.now(),
                    affected_spare_part=form.clean_spare_part_id(),
                    required_quantity=form.cleaned_data.get('required_quantity'),
                    created_by=request.user.flotauser if hasattr(request.user, 'flotauser') else None
                )

                # Si es pausa por stock, obtener cantidad disponible
                if pause.affected_spare_part:
                    try:
                        from repuestos.models import SparePartStock
                        stock_info = SparePartStock.objects.get(repuesto=pause.affected_spare_part)
                        pause.available_quantity = stock_info.current_stock
                    except:
                        pass

                pause.save()
                messages.success(request, 'Pausa rápida registrada exitosamente.')
                
            return redirect('pausas:work_order_pause_list')
    else:
        form = QuickPauseForm()

    return render(request, 'pausas/quick_pause_form.html', {
        'form': form,
        'title': 'Pausa Rápida'
    })


# API para AJAX
@login_required
def ajax_load_mechanics(request):
    """Obtener mecánicos asignados a una OT para AJAX"""
    work_order_id = request.GET.get('work_order_id')
    if not work_order_id:
        return JsonResponse({'error': 'work_order_id is required'}, status=400)

    mechanics = WorkOrderMechanic.objects.filter(
        work_order_id=work_order_id,
        is_active=True
    ).select_related('mechanic').values(
        'id_mechanic_assignment',
        'mechanic__name'
    )

    mechanics_list = list(mechanics)
    return JsonResponse({'mechanics': mechanics_list})


@login_required
def ajax_load_spare_parts(request):
    """Obtener repuestos utilizados en una OT para AJAX"""
    work_order_id = request.GET.get('work_order_id')
    if not work_order_id:
        return JsonResponse({'error': 'work_order_id is required'}, status=400)

    try:
        work_order = WorkOrder.objects.get(id_work_order=work_order_id)
        spare_parts = work_order.spare_part_usages.select_related('repuesto').values(
            'repuesto__id_repuesto',
            'repuesto__name',
            'quantity_used'
        )
        spare_parts_list = list(spare_parts)
        return JsonResponse({'spare_parts': spare_parts_list})
    except WorkOrder.DoesNotExist:
        return JsonResponse({'error': 'Work order not found'}, status=404)
