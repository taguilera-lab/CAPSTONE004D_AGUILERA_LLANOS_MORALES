from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from documents.models import Ingreso, MaintenanceSchedule, Vehicle, Route, WorkOrder, WorkOrderStatus, WorkOrderMechanic, SparePartUsage, Repuesto, Task, Incident, IngresoImage
from repuestos.models import SparePartStock
from .forms import IngresoForm, AgendarIngresoForm, WorkOrderForm, WorkOrderMechanicForm, SparePartUsageForm
from django.utils.safestring import mark_safe
from django.utils import timezone
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
    ).prefetch_related('work_orders').all()
    return render(request, 'agenda/ingresos_list.html', {'ingresos': ingresos})

def ingreso_create_select(request):
    from datetime import date, datetime
    
    # Obtener la fecha seleccionada
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Si se especifica un parámetro 'date' y 'schedule_id', mostrar captura de fotos para ese agendamiento específico
    if request.GET.get('date') and request.GET.get('schedule_id'):
        schedule_id = request.GET.get('schedule_id')
        # Filtrar solo el agendamiento específico
        pending_schedules = MaintenanceSchedule.objects.filter(
            id_schedule=schedule_id,
            ingresos__isnull=True,
            start_datetime__date=selected_date
        ).select_related('patent', 'expected_chofer', 'assigned_user', 'patent__site')
        
        return render(request, 'agenda/ingreso_create_with_photos.html', {
            'pending_schedules': pending_schedules,
            'selected_date': selected_date,
        })
    
    # Si se especifica un parámetro 'date' y 'show_schedules', mostrar lista de selección filtrada
    if request.GET.get('date') and request.GET.get('show_schedules'):
        # Filtrar agendamientos pendientes para la fecha seleccionada
        pending_schedules = MaintenanceSchedule.objects.filter(
            ingresos__isnull=True,
            start_datetime__date=selected_date
        ).select_related('patent', 'expected_chofer', 'assigned_user', 'patent__site').order_by('start_datetime')
        
        # Fechas disponibles (con agendamientos pendientes)
        available_dates = MaintenanceSchedule.objects.filter(
            ingresos__isnull=True
        ).dates('start_datetime', 'day')
        
        return render(request, 'agenda/ingreso_create_select.html', {
            'pending_schedules': pending_schedules,
            'selected_date': selected_date,
            'available_dates': available_dates,
        })
    
    # Si se especifica un parámetro 'date', mostrar lista de agendamientos para esa fecha
    if request.GET.get('date'):
        # Filtrar agendamientos pendientes para la fecha seleccionada
        pending_schedules = MaintenanceSchedule.objects.filter(
            ingresos__isnull=True,
            start_datetime__date=selected_date
        ).select_related('patent', 'expected_chofer', 'assigned_user', 'patent__site').order_by('start_datetime')
        
        # Fechas disponibles (con agendamientos pendientes)
        available_dates = MaintenanceSchedule.objects.filter(
            ingresos__isnull=True
        ).dates('start_datetime', 'day')
        
        return render(request, 'agenda/ingreso_create_select.html', {
            'pending_schedules': pending_schedules,
            'selected_date': selected_date,
            'available_dates': available_dates,
        })
    
    # Comportamiento original: mostrar lista de agendamientos
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
    # Obtener imágenes relacionadas con el ingreso
    images = ingreso.images.all().order_by('-uploaded_at')
    # Obtener incidentes relacionados con el agendamiento (si existe) y con el ingreso directamente
    related_incidents = []
    
    # Incidentes relacionados con el schedule del ingreso
    if ingreso.schedule:
        related_incidents.extend(ingreso.schedule.related_incidents.all())
    
    # Incidentes relacionados directamente con el ingreso
    direct_incidents = ingreso.incidents.all()
    related_incidents.extend(direct_incidents)
    
    # Eliminar duplicados y ordenar por fecha de reporte (más reciente primero)
    seen_ids = set()
    unique_incidents = []
    for incident in sorted(related_incidents, key=lambda x: x.reported_at, reverse=True):
        if incident.id_incident not in seen_ids:
            unique_incidents.append(incident)
            seen_ids.add(incident.id_incident)
    
    return render(request, 'agenda/ingreso_detail.html', {
        'ingreso': ingreso, 
        'schedules': schedules, 
        'images': images,
        'related_incidents': unique_incidents
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
    routes = list(Route.objects.values('id_route', 'route_code'))
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
        
        # Validar que el schedule tenga un vendedor asignado
        if not schedule.expected_chofer:
            from django.contrib import messages
            messages.error(request, f'No se puede crear el ingreso porque el agendamiento {schedule.patent} no tiene un vendedor asignado.')
            return redirect('ingreso_create_select')
        
        # Crear el ingreso basado en el agendamiento
        ingreso = Ingreso.objects.create(
            patent=schedule.patent,
            entry_datetime=timezone.now(),
            chofer=schedule.expected_chofer,
            observations=schedule.observations,
            schedule=schedule,
            authorization=False  # Por defecto no autorizado hasta la salida
        )
        
        # Registrar quién creó el ingreso
        if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'flotauser'):
            ingreso.entry_registered_by = request.user.flotauser
            ingreso.save()
        
        # Procesar imágenes si se subieron
        images = request.FILES.getlist('images')
        for i, image_file in enumerate(images):
            # Generar nombre automático para la imagen
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_name = f"Ingreso_{ingreso.id_ingreso}_{timestamp}_{i+1}"
            
            # Crear la instancia de IngresoImage
            ingreso_image = IngresoImage.objects.create(
                ingreso=ingreso,
                name=image_name,
                image=image_file,
                uploaded_by=request.user.flotauser if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'flotauser') else None
            )
        
        # Mensaje de éxito
        from django.contrib import messages
        vendedor_name = schedule.expected_chofer.name if schedule.expected_chofer else "Vendedor por asignar"
        fecha_formateada = timezone.now().strftime("%d/%m/%Y %H:%M")
        messages.success(
            request, 
            f'Ingreso creado exitosamente: {schedule.patent} - {fecha_formateada} - {vendedor_name}'
        )
        
        return redirect('ingresos_list')
    
    # Si no es POST, redirigir a la página de selección
    return redirect('ingreso_create_select')


def orden_trabajo_list(request):
    """Vista para listar todas las órdenes de trabajo"""
    # Obtener todas las órdenes de trabajo con sus ingresos relacionados (si existen)
    work_orders = WorkOrder.objects.select_related(
        'ingreso__patent', 'ingreso__chofer', 'ingreso__patent__site', 'status'
    ).prefetch_related('diagnostics__incidents__vehicle').order_by('-created_datetime')

    # Obtener estados para el filtro
    work_order_statuses = WorkOrderStatus.objects.all()

    # Crear una lista con información de todas las órdenes de trabajo
    work_orders_data = []
    for work_order in work_orders:
        # Si no hay ingreso, intentar obtener el vehículo del diagnóstico
        vehicle = None
        if not work_order.ingreso:
            # Buscar el diagnóstico relacionado
            diagnostic = work_order.diagnostics.first()
            if diagnostic:
                # Obtener el primer incidente del diagnóstico
                incident = diagnostic.incidents.first()
                if incident:
                    vehicle = incident.vehicle

        work_orders_data.append({
            'ingreso': work_order.ingreso,  # Puede ser None
            'work_order': work_order,
            'vehicle': vehicle,  # Vehículo del diagnóstico si no hay ingreso
            'has_work_order': True,  # Siempre es True ya que estamos iterando sobre work_orders
            'status_name': work_order.status.name if work_order.status else 'Sin Estado',
            'status_color': work_order.status.color if work_order.status else '#6c757d',
        })

    return render(request, 'agenda/orden_trabajo_list.html', {
        'work_orders_data': work_orders_data,
        'work_order_statuses': work_order_statuses,
    })


def orden_trabajo_create(request, ingreso_id):
    """Vista para crear una nueva orden de trabajo para un ingreso"""
    ingreso = get_object_or_404(Ingreso, id_ingreso=ingreso_id)

    # Verificar si ya existe una orden de trabajo para este ingreso
    if ingreso.work_orders.exists():
        from django.contrib import messages
        messages.warning(request, f'Ya existe una orden de trabajo para el ingreso {ingreso.id_ingreso}')
        return redirect('orden_trabajo_detail', work_order_id=ingreso.work_orders.first().id_work_order)

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

    # Obtener imágenes de la orden de trabajo
    work_order_images = work_order.images.all().order_by('-uploaded_at')

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
        'work_order_images': work_order_images,
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
            
            # Obtener el costo unitario del stock del repuesto
            try:
                stock_info = SparePartStock.objects.get(repuesto=spare_part_usage.repuesto)
                unit_cost = stock_info.unit_cost
            except SparePartStock.DoesNotExist:
                # Si no hay información de stock, usar costo 0
                unit_cost = 0
            
            spare_part_usage.unit_cost = unit_cost
            spare_part_usage.total_cost = spare_part_usage.quantity_used * unit_cost
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


@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(MaintenanceSchedule, pk=pk)
    
    # Obtener ingresos relacionados con este schedule
    related_ingresos = schedule.ingresos.all().order_by('-entry_datetime')
    
    # Obtener incidentes relacionados con este schedule
    related_incidents = schedule.related_incidents.all().order_by('-reported_at')
    
    return render(request, 'agenda/schedule_detail.html', {
        'schedule': schedule,
        'related_ingresos': related_ingresos,
        'related_incidents': related_incidents
    })


@login_required
def search_vehicle_api(request):
    """
    API para buscar información de un vehículo por patente
    """
    patent = request.GET.get('patent', '').strip().upper()
    
    if not patent:
        return JsonResponse({'found': False, 'error': 'Patente requerida'})
    
    try:
        vehicle = Vehicle.objects.select_related('site').prefetch_related('routes').get(patent=patent)
        
        # Obtener la ruta principal (primera ruta asociada)
        route_code = None
        routes = vehicle.routes.all()
        if routes.exists():
            route_code = routes.first().route_code
        
        vehicle_data = {
            'patent': vehicle.patent,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'site_name': vehicle.site.name if vehicle.site else None,
            'route_code': route_code
        }
        
        return JsonResponse({'found': True, 'vehicle': vehicle_data})
        
    except Vehicle.DoesNotExist:
        return JsonResponse({'found': False, 'error': 'Vehículo no encontrado'})
    except Exception as e:
        return JsonResponse({'found': False, 'error': str(e)})


def search_vehicles_autocomplete(request):
    """
    API para autocompletado de búsqueda de vehículos
    """
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'vehicles': []})

    # Buscar vehículos que coincidan con la consulta
    vehicles = Vehicle.objects.filter(
        Q(patent__icontains=query) |
        Q(brand__icontains=query) |
        Q(model__icontains=query)
    ).select_related('site')[:10]  # Limitar a 10 resultados

    vehicles_data = []
    for vehicle in vehicles:
        # Obtener la ruta principal
        route_code = None
        routes = vehicle.routes.all()
        if routes.exists():
            route_code = routes.first().route_code

        vehicles_data.append({
            'id': vehicle.patent,
            'patent': vehicle.patent,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'year': vehicle.year,
            'site_name': vehicle.site.name if vehicle.site else None,
            'route_code': route_code,
            'display_text': f"{vehicle.patent} - {vehicle.brand} {vehicle.model} ({vehicle.year})"
        })

    return JsonResponse({'vehicles': vehicles_data})


@login_required
def recepcionista_ingreso_tecnico(request):
    """
    Vista para que recepcionistas registren fotos técnicas de un ingreso existente
    """
    # Verificar que el usuario sea recepcionista
    if not (hasattr(request.user, 'flotauser') and request.user.flotauser.role.name == 'Recepcionista de Vehículos'):
        return redirect('home')

    # Obtener el ingreso_id de los parámetros
    ingreso_id = request.GET.get('ingreso_id')
    if not ingreso_id:
        return render(request, 'agenda/ingreso_tecnico.html', {
            'error': 'Debe especificar un ingreso válido.'
        })

    # Obtener el ingreso
    try:
        ingreso = Ingreso.objects.select_related('patent', 'patent__site', 'schedule').get(id_ingreso=ingreso_id)
    except Ingreso.DoesNotExist:
        return render(request, 'agenda/ingreso_tecnico.html', {
            'error': 'El ingreso especificado no existe.'
        })

    if request.method == 'POST':
        # Procesar las imágenes subidas para el ingreso existente
        photo_descriptions = [
            'Estado frontal del vehículo',
            'Estado lateral izquierdo',
            'Estado lateral derecho',
            'Estado trasero',
            'Estado del motor',
            'Estado de neumáticos',
            'Daños externos visibles'
        ]

        uploaded_images = []
        for i, description in enumerate(photo_descriptions):
            photo_key = f'photo_{i}'
            if photo_key in request.FILES:
                image_file = request.FILES[photo_key]
                ingreso_image = IngresoImage.objects.create(
                    ingreso=ingreso,
                    name=f"Foto {i+1} - {description}",
                    description=description,
                    image=image_file,
                    uploaded_by=request.user.flotauser
                )
                uploaded_images.append(ingreso_image)

        # Marcar que el ingreso tiene fotos técnicas completadas
        ingreso.es_ingreso_tecnico = True
        ingreso.save()

        # Actualizar las observaciones del ingreso para indicar que es técnico
        if not ingreso.observations or "Ingreso técnico" not in ingreso.observations:
            ingreso.observations = f"{ingreso.observations or ''}\n[Ingreso técnico registrado por {request.user.flotauser.name}]".strip()
            ingreso.save()

        # Redireccionar al detalle del ingreso
        return redirect('ingreso_detail', pk=ingreso.id_ingreso)

    # GET request - mostrar detalles del ingreso y formulario de fotos
    # Obtener rutas del vehículo
    routes = ingreso.patent.routes.all()

    context = {
        'ingreso': ingreso,
        'vehicle': ingreso.patent,
        'routes': routes,
        'has_schedule': ingreso.schedule is not None,
    }

    return render(request, 'agenda/ingreso_tecnico.html', context)


@login_required
def orden_trabajo_add_photo(request, work_order_id):
    """Vista para agregar fotos a una orden de trabajo"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No se pueden agregar fotos a una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        # Procesar las fotos subidas (desde archivo)
        images = request.FILES.getlist('images')
        file_description = request.POST.get('file_description', '')

        # Procesar las fotos capturadas desde la cámara
        captured_images = request.FILES.getlist('captured_images')
        captured_names = request.POST.getlist('captured_names')
        captured_descriptions = request.POST.getlist('captured_descriptions')

        # Combinar todas las fotos
        all_images = list(images) + list(captured_images)
        all_descriptions = []

        # Para fotos desde archivo, usar la descripción general
        for _ in images:
            all_descriptions.append(file_description)

        # Para fotos capturadas, usar las descripciones individuales
        all_descriptions.extend(captured_descriptions)

        if not all_images:
            from django.contrib import messages
            messages.error(request, 'Debe capturar al menos una foto con la cámara o seleccionar archivos.')
            return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

        # Importar el modelo WorkOrderImage
        from documents.models import WorkOrderImage

        for i, image_file in enumerate(all_images):
            # Determinar el nombre de la foto
            if i < len(images):
                # Foto desde archivo - usar nombre original o generar uno
                base_name = image_file.name.rsplit('.', 1)[0] if '.' in image_file.name else 'foto_archivo'
                image_name = f"{base_name}_{i+1}"
            else:
                # Foto capturada - usar el nombre proporcionado o generar uno
                captured_index = i - len(images)
                image_name = captured_names[captured_index] if captured_index < len(captured_names) and captured_names[captured_index] else f"Foto {i+1}"

            # Obtener la descripción correspondiente
            description = all_descriptions[i] if i < len(all_descriptions) else ''

            # Crear la instancia de WorkOrderImage
            work_order_image = WorkOrderImage.objects.create(
                work_order=work_order,
                name=image_name,
                description=description,
                image=image_file,
                uploaded_by=request.user.flotauser if hasattr(request.user, 'flotauser') else None
            )

        from django.contrib import messages
        messages.success(request, f'Se agregaron {len(all_images)} foto(s) exitosamente a la orden de trabajo OT-{work_order.id_work_order}')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    # GET request - mostrar formulario para subir fotos
    # Obtener mecánicos asignados
    mechanic_assignments = work_order.mechanic_assignments.select_related('mechanic').filter(is_active=True)
    
    return render(request, 'agenda/orden_trabajo_add_photo.html', {
        'work_order': work_order,
        'mechanic_assignments': mechanic_assignments,
    })


@login_required
def orden_trabajo_add_tasks_auto(request, work_order_id):
    """Vista para agregar tareas automáticamente a los mecánicos asignados"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes agregar tareas a una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    # Obtener mecánicos asignados
    mechanic_assignments = work_order.mechanic_assignments.select_related('mechanic').filter(is_active=True)

    if not mechanic_assignments:
        from django.contrib import messages
        messages.warning(request, 'No hay mecánicos asignados a esta orden de trabajo')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        # Procesar las horas enviadas
        import random
        from datetime import timedelta

        # Lista de descripciones posibles para tareas
        task_descriptions = [
            "Revisar sistema de frenos",
            "Inspeccionar motor y componentes",
            "Verificar sistema eléctrico",
            "Chequear suspensión y dirección",
            "Revisar transmisión",
            "Inspeccionar sistema de escape",
            "Verificar neumáticos y ruedas",
            "Chequear sistema de refrigeración",
            "Revisar batería y alternador",
            "Inspeccionar sistema de combustible",
            "Verificar luces y señales",
            "Chequear aire acondicionado",
            "Revisar frenos de mano",
            "Inspeccionar amortiguadores",
            "Verificar correas y mangueras"
        ]

        urgencies = ['Alta', 'Media', 'Baja']

        # Obtener service_types disponibles
        from documents.models import ServiceType
        service_types = list(ServiceType.objects.all())

        tasks_created = 0
        for assignment in mechanic_assignments:
            # Generar datos aleatorios
            description = random.choice(task_descriptions)
            urgency = random.choice(urgencies)
            service_type = random.choice(service_types) if service_types else None

            # Obtener horas del POST
            hours_key = f'hours_{assignment.id_assignment}'
            hours = request.POST.get(hours_key)
            try:
                hours = float(hours) if hours else 0
            except ValueError:
                hours = 0

            # Crear la tarea
            start_datetime = timezone.now()
            end_datetime = start_datetime + timedelta(hours=hours) if hours > 0 else None

            task = Task.objects.create(
                work_order=work_order,
                description=description,
                urgency=urgency,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                service_type=service_type,
                supervisor=work_order.supervisor
            )

            # Asignar la tarea al mecánico
            from documents.models import TaskAssignment
            TaskAssignment.objects.create(
                task=task,
                user=assignment.mechanic
            )

            tasks_created += 1

        from django.contrib import messages
        messages.success(request, f'Se crearon {tasks_created} tarea(s) automáticamente para los mecánicos asignados')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    # GET request - mostrar formulario con tareas generadas
    import random

    # Lista de descripciones posibles para tareas
    task_descriptions = [
        "Revisar sistema de frenos",
        "Inspeccionar motor y componentes",
        "Verificar sistema eléctrico",
        "Chequear suspensión y dirección",
        "Revisar transmisión",
        "Inspeccionar sistema de escape",
        "Verificar neumáticos y ruedas",
        "Chequear sistema de refrigeración",
        "Revisar batería y alternador",
        "Inspeccionar sistema de combustible",
        "Verificar luces y señales",
        "Chequear aire acondicionado",
        "Revisar frenos de mano",
        "Inspeccionar amortiguadores",
        "Verificar correas y mangueras"
    ]

    urgencies = ['Alta', 'Media', 'Baja']

    # Obtener service_types disponibles
    from documents.models import ServiceType
    service_types = list(ServiceType.objects.all())

    # Generar tareas aleatorias para mostrar (sin guardar)
    generated_tasks = []
    for assignment in mechanic_assignments:
        description = random.choice(task_descriptions)
        urgency = random.choice(urgencies)
        service_type = random.choice(service_types) if service_types else None

        generated_tasks.append({
            'assignment': assignment,
            'description': description,
            'urgency': urgency,
            'service_type': service_type.name if service_type else 'General'
        })

    return render(request, 'agenda/orden_trabajo_add_tasks_auto.html', {
        'work_order': work_order,
        'mechanic_assignments': mechanic_assignments,
        'generated_tasks': generated_tasks,
    })


@login_required
def orden_trabajo_edit_task(request, task_id):
    """Vista para editar una tarea específica"""
    from documents.models import Task, TaskAssignment

    task = get_object_or_404(Task, id_task=task_id)

    # Verificar que la tarea pertenezca a una orden de trabajo activa
    if not task.work_order or task.work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes editar tareas de órdenes de trabajo completadas')
        return redirect('orden_trabajo_detail', work_order_id=task.work_order.id_work_order)

    # Obtener la asignación de la tarea
    try:
        task_assignment = TaskAssignment.objects.select_related('user').get(task=task)
        assigned_mechanic = task_assignment.user
    except TaskAssignment.DoesNotExist:
        assigned_mechanic = None

    if request.method == 'POST':
        # Procesar el formulario
        description = request.POST.get('description')
        urgency = request.POST.get('urgency')
        hours = request.POST.get('hours')

        # Validar datos
        if not description or not urgency:
            from django.contrib import messages
            messages.error(request, 'La descripción y urgencia son obligatorias')
            return redirect('orden_trabajo_edit_task', task_id=task.id_task)

        try:
            hours = float(hours) if hours else 0
        except ValueError:
            hours = 0

        # Actualizar la tarea
        task.description = description
        task.urgency = urgency

        if hours > 0:
            from datetime import timedelta
            task.end_datetime = task.start_datetime + timedelta(hours=hours)
        else:
            task.end_datetime = None

        task.save()

        from django.contrib import messages
        messages.success(request, 'Tarea actualizada exitosamente')
        return redirect('orden_trabajo_detail', work_order_id=task.work_order.id_work_order)

    # GET request - mostrar formulario de edición
    # Calcular horas actuales si existe end_datetime
    current_hours = 0
    if task.end_datetime:
        from datetime import timedelta
        duration = task.end_datetime - task.start_datetime
        current_hours = duration.total_seconds() / 3600  # Convertir a horas

    return render(request, 'agenda/orden_trabajo_edit_task.html', {
        'task': task,
        'assigned_mechanic': assigned_mechanic,
        'current_hours': current_hours,
    })


@login_required
def orden_trabajo_assign_supervisor(request, work_order_id):
    """Vista para asignar o cambiar jefe de taller a una orden de trabajo"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes cambiar el jefe de taller de una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        supervisor_id = request.POST.get('supervisor_id')

        if supervisor_id:
            try:
                from documents.models import FlotaUser
                supervisor = FlotaUser.objects.get(id_user=supervisor_id)
                work_order.supervisor = supervisor
                work_order.save()

                from django.contrib import messages
                messages.success(request, f'Jefe de taller {supervisor.name} asignado exitosamente a la orden de trabajo')
                return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)
            except FlotaUser.DoesNotExist:
                from django.contrib import messages
                messages.error(request, 'Supervisor no encontrado')
        else:
            from django.contrib import messages
            messages.error(request, 'Debes seleccionar un supervisor')

    # GET request - mostrar formulario para seleccionar jefe de taller
    # Obtener usuarios con rol de jefe de taller
    from documents.models import FlotaUser, Role
    try:
        jefe_taller_role = Role.objects.get(name='Jefe de taller')
        available_jefes_taller = FlotaUser.objects.filter(role=jefe_taller_role).order_by('name')
    except Role.DoesNotExist:
        # Si no existe el rol específico, mostrar todos los usuarios activos
        available_jefes_taller = FlotaUser.objects.filter(status__name='Activo').order_by('name')

    return render(request, 'agenda/orden_trabajo_assign_supervisor.html', {
        'work_order': work_order,
        'available_jefes_taller': available_jefes_taller,
        'current_supervisor': work_order.supervisor,
    })


def orden_trabajo_assign_service_type(request, work_order_id):
    """Vista para asignar o cambiar tipo de servicio a una orden de trabajo"""
    work_order = get_object_or_404(WorkOrder, id_work_order=work_order_id)

    # Verificar si la orden está completada
    if work_order.status.name == 'Completada':
        from django.contrib import messages
        messages.error(request, 'No puedes cambiar el tipo de servicio de una orden de trabajo completada')
        return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)

    if request.method == 'POST':
        service_type_id = request.POST.get('service_type_id')

        if service_type_id:
            try:
                from documents.models import ServiceType
                service_type = ServiceType.objects.get(id_service_type=service_type_id)
                work_order.service_type = service_type
                work_order.save()

                from django.contrib import messages
                messages.success(request, f'Tipo de servicio "{service_type.name}" asignado exitosamente a la orden de trabajo')
                return redirect('orden_trabajo_detail', work_order_id=work_order.id_work_order)
            except ServiceType.DoesNotExist:
                from django.contrib import messages
                messages.error(request, 'Tipo de servicio no encontrado')
        else:
            from django.contrib import messages
            messages.error(request, 'Debes seleccionar un tipo de servicio')

    # GET request - mostrar formulario para seleccionar tipo de servicio
    # Obtener todos los tipos de servicio disponibles
    from documents.models import ServiceType
    available_service_types = ServiceType.objects.all().order_by('name')

    return render(request, 'agenda/orden_trabajo_assign_service_type.html', {
        'work_order': work_order,
        'available_service_types': available_service_types,
        'current_service_type': work_order.service_type,
    })
