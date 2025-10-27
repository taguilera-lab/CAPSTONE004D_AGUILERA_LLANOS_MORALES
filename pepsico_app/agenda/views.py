from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from documents.models import Ingreso, MaintenanceSchedule, Vehicle, Route, WorkOrder, WorkOrderStatus, WorkOrderMechanic, SparePartUsage, Repuesto, Task, Incident
from .forms import IngresoForm, AgendarIngresoForm, WorkOrderForm, WorkOrderMechanicForm, SparePartUsageForm
from django.utils.safestring import mark_safe
import json

def calendario(request):
    schedules = MaintenanceSchedule.objects.prefetch_related('related_incidents', 'ingresos').all()
    
    # Crear una lista de eventos serializable
    events_list = []
    for schedule in schedules:
        # Obtener incidentes relacionados
        related_incidents = []
        for incident in schedule.related_incidents.all():
            related_incidents.append({
                'id': incident.id_incident,
                'name': incident.name,
                'type': incident.incident_type,
                'description': incident.description or '',
                'priority': incident.priority or 'Normal',
                'is_emergency': incident.is_emergency,
                'reported_at': incident.reported_at.strftime('%Y-%m-%d %H:%M'),
            })
        
        # Verificar si ya tiene un ingreso asociado
        has_ingreso = schedule.ingresos.exists()
        
        events_list.append({
            'id': schedule.id_schedule,
            'title': f"{schedule.patent} - Servicio de mantenimiento",
            'start': schedule.start_datetime.isoformat(),
            'end': None,
            'description': schedule.observations or '',
            'patent': str(schedule.patent),
            'assigned_user': schedule.assigned_user.name if schedule.assigned_user else '',
            'status': schedule.status.name if schedule.status else '',
            'related_incidents': related_incidents,
            'has_ingreso': has_ingreso,
        })
    
    # Usar json.dumps con manejo de errores
    try:
        events_json = json.dumps(events_list, ensure_ascii=True, default=str)
        return render(request, 'agenda/calendario.html', {'events': mark_safe(events_json)})
    except (TypeError, ValueError) as e:
        # Si hay error, devolver lista vacía
        print(f"Error serializando eventos: {e}")
        return render(request, 'agenda/calendario.html', {'events': mark_safe('[]')})

def ingresos_list(request):
    ingresos = Ingreso.objects.select_related(
        'patent', 'patent__site', 'entry_registered_by', 'exit_registered_by', 'schedule'
    ).prefetch_related('work_order').all()
    return render(request, 'agenda/ingresos_list.html', {'ingresos': ingresos})

def ingreso_create_select(request):
    from datetime import date, datetime
    
    # Obtener la fecha seleccionada o usar hoy por defecto
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Filtrar agendamientos pendientes para la fecha seleccionada
    pending_schedules = MaintenanceSchedule.objects.filter(
        ingresos__isnull=True,
        start_datetime__date=selected_date
    ).select_related('patent').order_by('start_datetime')
    
    # Fechas disponibles (con agendamientos pendientes)
    available_dates = MaintenanceSchedule.objects.filter(
        ingresos__isnull=True
    ).dates('start_datetime', 'day')
    
    return render(request, 'agenda/ingreso_create_select.html', {
        'pending_schedules': pending_schedules,
        'selected_date': selected_date,
        'available_dates': available_dates,
    })

def ingreso_detail(request, pk):
    ingreso = get_object_or_404(Ingreso, pk=pk)
    # Relacionar con agendamientos por patent
    schedules = MaintenanceSchedule.objects.filter(patent=ingreso.patent)
    return render(request, 'agenda/ingreso_detail.html', {'ingreso': ingreso, 'schedules': schedules})

def ingreso_create(request):
    vehicles = list(Vehicle.objects.values('patent', 'site__name'))
    routes = list(Route.objects.values('id_route', 'route_code', 'truck'))
    
    # Buscar agendamiento relacionado
    related_schedule = None
    schedule_id = request.GET.get('schedule_id')
    patent_param = request.GET.get('patent')
    
    if schedule_id:
        # Si se proporciona schedule_id específico
        related_schedule = get_object_or_404(MaintenanceSchedule, id_schedule=schedule_id, ingresos__isnull=True)
    elif patent_param:
        # Si se proporciona patente (desde calendario)
        try:
            vehicle = Vehicle.objects.get(patent=patent_param)
            # Buscar agendamiento más reciente sin ingreso asociado
            related_schedule = MaintenanceSchedule.objects.filter(
                patent=vehicle,
                ingresos__isnull=True
            ).order_by('-start_datetime').first()
        except Vehicle.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = IngresoForm(request.POST)
        if form.is_valid():
            ingreso = form.save(commit=False)
            
            # Buscar agendamiento para esta patente en un rango de tiempo razonable
            from datetime import timedelta
            start_time = ingreso.entry_datetime - timedelta(hours=2)
            end_time = ingreso.entry_datetime + timedelta(hours=2)
            
            related_schedule = MaintenanceSchedule.objects.filter(
                patent=ingreso.patent,
                start_datetime__range=(start_time, end_time),
                ingresos__isnull=True  # Solo agendamientos sin ingreso asociado
            ).first()
            
            if related_schedule:
                ingreso.schedule = related_schedule
                # Pre-llenar información del agendamiento
                if not ingreso.chofer and related_schedule.expected_chofer:
                    ingreso.chofer = related_schedule.expected_chofer
                if not ingreso.observations and related_schedule.observations:
                    ingreso.observations = related_schedule.observations
            
            # Registrar quién creó el ingreso (cuando haya autenticación)
            if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'flotauser'):
                ingreso.entry_registered_by = request.user.flotauser
            
            ingreso.save()
            return redirect('ingresos_list')
    else:
        # Pre-llenar formulario si hay agendamiento relacionado
        if related_schedule:
            initial_data = {
                'patent': related_schedule.patent,
                'entry_datetime': related_schedule.start_datetime,
                'chofer': related_schedule.expected_chofer,  # Pre-llenar chofer con el esperado
                'observations': related_schedule.observations,
            }
            form = IngresoForm(initial=initial_data)
        else:
            form = IngresoForm()
    
    return render(request, 'agenda/ingreso_form.html', {
        'form': form, 
        'vehicles': json.dumps(vehicles), 
        'routes': json.dumps(routes),
        'related_schedule': related_schedule
    })

def registrar_salida(request):
    if request.method == 'POST':
        ingreso_id = request.POST.get('ingreso')
        exit_datetime = request.POST.get('exit_datetime')
        autorizar = request.POST.get('autorizar') == 'on'
        ingreso = get_object_or_404(Ingreso, id_ingreso=ingreso_id, exit_datetime__isnull=True)
        if autorizar:
            ingreso.authorization = True
            ingreso.exit_datetime = exit_datetime
            # Asumir que request.user es FlotaUser o agregar lógica
            # ingreso.exit_registered_by = request.user.flotauser  # Ajustar según auth
            ingreso.save()
            return redirect('ingresos_list')
        else:
            return render(request, 'agenda/registrar_salida.html', {
                'ingresos_pendientes': Ingreso.objects.filter(exit_datetime__isnull=True),
                'error': 'Debe autorizar la salida para registrar.'
            })
    else:
        ingresos_pendientes = Ingreso.objects.filter(exit_datetime__isnull=True)
        return render(request, 'agenda/registrar_salida.html', {'ingresos_pendientes': ingresos_pendientes})


@login_required
def agendar_ingreso(request):
    # Verificar que el usuario tenga rol "vendedor"
    if not (hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'flotauser') and request.user.flotauser.role.name == 'Vendedor'):
        from django.contrib import messages
        messages.error(request, 'No tienes permisos para agendar ingresos. Solo usuarios con rol Vendedor pueden acceder a esta funcionalidad.')
        return redirect('calendario')
    
    vehicles = list(Vehicle.objects.values('patent', 'site__name'))
    routes = list(Route.objects.values('id_route', 'route_code', 'truck'))
    if request.method == 'POST':
        form = AgendarIngresoForm(request.POST, user=request.user if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'flotauser') else None)
        if form.is_valid():
            schedule = form.save()  # El formulario ya asigna assigned_user automáticamente
            return redirect('calendario')
    else:
        # Pre-llenar el chofer con el usuario actual si está disponible
        form = AgendarIngresoForm(user=request.user if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'flotauser') else None)
    
        return render(request, 'agenda/agendar_ingreso.html', {'form': form, 'vehicles': json.dumps(vehicles), 'routes': json.dumps(routes)})


def ingreso_create_from_schedule(request):
    """Vista para crear un ingreso directamente desde un agendado confirmado"""
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        
        if not schedule_id:
            from django.contrib import messages
            messages.error(request, 'ID de agendamiento no proporcionado.')
            return redirect('ingreso_create_select')
        
        # Obtener el agendamiento
        schedule = get_object_or_404(MaintenanceSchedule, id_schedule=schedule_id, ingresos__isnull=True)
        
        # Validar que el schedule tenga un chofer asignado
        if not schedule.expected_chofer:
            from django.contrib import messages
            messages.error(request, f'No se puede crear el ingreso porque el agendamiento {schedule.patent} no tiene un chofer asignado.')
            return redirect('ingreso_create_select')
        
        # Crear el ingreso basado en el agendamiento
        ingreso = Ingreso.objects.create(
            patent=schedule.patent,
            entry_datetime=schedule.start_datetime,
            chofer=schedule.expected_chofer,
            observations=schedule.observations,
            schedule=schedule,
            authorization=False  # Por defecto no autorizado hasta la salida
        )
        
        # Registrar quién creó el ingreso
        if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'flotauser'):
            ingreso.entry_registered_by = request.user.flotauser
            ingreso.save()
        
        # Mensaje de éxito
        from django.contrib import messages
        chofer_name = schedule.expected_chofer.name if schedule.expected_chofer else "Chofer por asignar"
        fecha_formateada = schedule.start_datetime.strftime("%d/%m/%Y %H:%M")
        messages.success(
            request, 
            f'Ingreso agendado confirmado: {schedule.patent} - {fecha_formateada} - {chofer_name}'
        )
        
        return redirect('ingresos_list')
    
    # Si no es POST, redirigir a la página de selección
    return redirect('ingreso_create_select')


def orden_trabajo_list(request):
    """Vista para listar todas las órdenes de trabajo"""
    # Obtener todos los ingresos que pueden tener órdenes de trabajo
    ingresos = Ingreso.objects.select_related('patent', 'chofer', 'patent__site').order_by('-entry_datetime')

    # Obtener estados para el filtro
    work_order_statuses = WorkOrderStatus.objects.all()

    # Crear una lista con información combinada de ingresos y órdenes de trabajo
    work_orders_data = []
    for ingreso in ingresos:
        work_order = getattr(ingreso, 'work_order', None)
        work_orders_data.append({
            'ingreso': ingreso,
            'work_order': work_order,
            'has_work_order': work_order is not None,
            'status_name': work_order.status.name if work_order else 'Sin Orden',
            'status_color': work_order.status.color if work_order else '#6c757d',
        })

    return render(request, 'agenda/orden_trabajo_list.html', {
        'work_orders_data': work_orders_data,
        'work_order_statuses': work_order_statuses,
    })


def orden_trabajo_create(request, ingreso_id):
    """Vista para crear una nueva orden de trabajo para un ingreso"""
    ingreso = get_object_or_404(Ingreso, id_ingreso=ingreso_id)

    # Verificar si ya existe una orden de trabajo para este ingreso
    if hasattr(ingreso, 'work_order'):
        from django.contrib import messages
        messages.warning(request, f'Ya existe una orden de trabajo para el ingreso {ingreso.id_ingreso}')
        return redirect('orden_trabajo_detail', work_order_id=ingreso.work_order.id_work_order)

    if request.method == 'POST':
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.ingreso = ingreso

            # Establecer estado por defecto si no se especificó
            if not work_order.status:
                default_status = WorkOrderStatus.objects.filter(name='Pendiente').first()
                if not default_status:
                    default_status = WorkOrderStatus.objects.create(
                        name='Pendiente',
                        description='Orden de trabajo creada, pendiente de asignación',
                        color='#ffc107'
                    )
                work_order.status = default_status

            # Asignar usuario creador si está disponible
            if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'flotauser'):
                work_order.created_by = request.user.flotauser

            work_order.save()

            from django.contrib import messages
            messages.success(request, f'Orden de trabajo OT-{work_order.id_work_order} creada exitosamente')
            return redirect('ingresos_list')
    else:
        form = WorkOrderForm()

    return render(request, 'agenda/orden_trabajo_create.html', {
        'form': form,
        'ingreso': ingreso,
    })


def orden_trabajo_detail(request, work_order_id):
    """Vista para ver y editar el detalle de una orden de trabajo"""
    work_order = get_object_or_404(
        WorkOrder.objects.select_related(
            'ingreso__patent', 'ingreso__chofer', 'ingreso__patent__site',
            'status', 'created_by', 'supervisor'
        ),
        id_work_order=work_order_id
    )

    # Obtener datos relacionados
    mechanic_assignments = work_order.mechanic_assignments.select_related('mechanic').filter(is_active=True)
    spare_part_usages = work_order.spare_part_usages.select_related('repuesto')
    tasks = Task.objects.filter(work_order=work_order).select_related('service_type', 'supervisor')

    # Obtener diagnósticos e incidentes asociados
    from documents.models import Diagnostics
    related_diagnostics = Diagnostics.objects.filter(
        related_work_order=work_order
    ).select_related('incident__vehicle', 'incident__reported_by', 'diagnostic_by').order_by('-diagnostic_started_at')

    # Formularios para agregar elementos
    mechanic_form = WorkOrderMechanicForm()
    spare_part_form = SparePartUsageForm()

    # Calcular totales
    total_mechanic_hours = sum(assignment.hours_worked for assignment in mechanic_assignments)
    total_spare_parts_cost = sum(usage.total_cost for usage in spare_part_usages)

    context = {
        'work_order': work_order,
        'mechanic_assignments': mechanic_assignments,
        'spare_part_usages': spare_part_usages,
        'tasks': tasks,
        'related_diagnostics': related_diagnostics,
        'mechanic_form': mechanic_form,
        'spare_part_form': spare_part_form,
        'total_mechanic_hours': total_mechanic_hours,
        'total_spare_parts_cost': total_spare_parts_cost,
    }

    return render(request, 'agenda/orden_trabajo_detail.html', context)


def orden_trabajo_update(request, work_order_id):
    """Vista para actualizar una orden de trabajo"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes editar una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        form = WorkOrderForm(request.POST, instance=work_order)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Orden de trabajo actualizada exitosamente')
            return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)
    else:
        form = WorkOrderForm(instance=work_order)

    return render(request, 'agenda/orden_trabajo_update.html', {
        'form': form,
        'work_order': work_order,
    })


def orden_trabajo_add_mechanic(request, work_order_id):
    """Vista para agregar un mecánico a una orden de trabajo"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes agregar mecánicos a una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        form = WorkOrderMechanicForm(request.POST)
        if form.is_valid():
            mechanic_assignment = form.save(commit=False)
            mechanic_assignment.work_order = work_order
            mechanic_assignment.save()

            from django.contrib import messages
            messages.success(request, f'Mecánico {mechanic_assignment.mechanic.name} asignado exitosamente')
            return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)
    else:
        form = WorkOrderMechanicForm()

    return render(request, 'agenda/orden_trabajo_add_mechanic.html', {
        'form': form,
        'work_order': work_order,
    })


def orden_trabajo_add_spare_part(request, work_order_id):
    """Vista para agregar un repuesto a una orden de trabajo"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes agregar repuestos a una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        form = SparePartUsageForm(request.POST)
        if form.is_valid():
            spare_part_usage = form.save(commit=False)
            spare_part_usage.work_order = work_order
            spare_part_usage.total_cost = spare_part_usage.quantity_used * spare_part_usage.unit_cost
            spare_part_usage.save()

            # Actualizar el costo total de la orden de trabajo
            work_order.total_cost += spare_part_usage.total_cost
            work_order.save()

            from django.contrib import messages
            messages.success(request, f'Repuesto {spare_part_usage.repuesto.name} agregado exitosamente')
            return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)
    else:
        form = SparePartUsageForm()

    return render(request, 'agenda/orden_trabajo_add_spare_part.html', {
        'form': form,
        'work_order': work_order,
    })


def orden_trabajo_delete_mechanics(request, work_order_id):
    """Vista para eliminar mecánicos seleccionados de una orden de trabajo"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes editar una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids')
        if selected_ids:
            # Eliminar las asignaciones de mecánicos seleccionadas
            deleted_count = WorkOrderMechanic.objects.filter(
                id_assignment__in=selected_ids,
                work_order=work_order
            ).delete()[0]

            from django.contrib import messages
            if deleted_count > 0:
                messages.success(request, f'{deleted_count} mecánico(s) eliminado(s) exitosamente')
            else:
                messages.warning(request, 'No se encontraron mecánicos para eliminar')
        else:
            messages.warning(request, 'No se seleccionaron mecánicos para eliminar')

    return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)


def orden_trabajo_delete_spare_parts(request, work_order_id):
    """Vista para eliminar piezas de repuesto seleccionadas de una orden de trabajo"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes editar una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids')
        if selected_ids:
            # Obtener los usos de repuestos antes de eliminarlos para actualizar el costo total
            spare_part_usages = SparePartUsage.objects.filter(
                id_usage__in=selected_ids,
                work_order=work_order
            )

            # Calcular el costo total a restar
            total_cost_to_subtract = sum(usage.total_cost for usage in spare_part_usages)

            # Eliminar los usos de repuestos
            deleted_count = spare_part_usages.delete()[0]

            # Actualizar el costo total de la orden de trabajo
            if total_cost_to_subtract > 0:
                work_order.total_cost -= total_cost_to_subtract
                work_order.save()

            from django.contrib import messages
            if deleted_count > 0:
                messages.success(request, f'{deleted_count} pieza(s) de repuesto eliminada(s) exitosamente')
            else:
                messages.warning(request, 'No se encontraron piezas de repuesto para eliminar')
        else:
            messages.warning(request, 'No se seleccionaron piezas de repuesto para eliminar')

    return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)


def orden_trabajo_complete(request, work_order_id):
    """Vista para marcar una orden de trabajo como completada"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    if request.method == 'POST':
        work_order.actual_completion = request.POST.get('actual_completion')
        completed_status = WorkOrderStatus.objects.filter(name='Completada').first()
        if completed_status:
            work_order.status = completed_status
        work_order.save()

        from django.contrib import messages
        messages.success(request, 'Orden de trabajo marcada como completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    return render(request, 'agenda/orden_trabajo_complete.html', {
        'work_order': work_order,
    })


def get_incidents_by_vehicle(request):
    """Vista AJAX para obtener incidentes de un vehículo específico"""
    from django.http import JsonResponse
    
    patent = request.GET.get('patent')
    if not patent:
        return JsonResponse({'error': 'Patente requerida'}, status=400)
    
    try:
        vehicle = Vehicle.objects.get(patent=patent)
        incidents = Incident.objects.filter(vehicle=vehicle).order_by('-reported_at')
        
        incidents_data = []
        for incident in incidents:
            incidents_data.append({
                'id': incident.id_incident,
                'name': incident.name,
                'incident_type': incident.incident_type,
                'description': incident.description[:100] + '...' if len(incident.description) > 100 else incident.description,
                'reported_at': incident.reported_at.strftime('%Y-%m-%d %H:%M'),
                'priority': incident.priority or 'Normal',
                'is_emergency': incident.is_emergency,
            })
        
        return JsonResponse({'incidents': incidents_data})
    
    except Vehicle.DoesNotExist:
        return JsonResponse({'error': 'Vehículo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
