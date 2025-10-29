from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from documents.models import Diagnostics, Incident, Vehicle, FlotaUser, Route
from .forms import DiagnosticsForm

@login_required
def diagnostics_list(request):
    """Vista para listar todos los diagnósticos"""
    # Filtrar diagnósticos según el rol del usuario
    if hasattr(request.user, 'flotauser'):
        user_role = request.user.flotauser.role.name
        if user_role == 'Mecánico':
            # Mecánicos solo ven diagnósticos asignados a ellos
            diagnostics = Diagnostics.objects.filter(assigned_to=request.user.flotauser)
        elif user_role == 'Jefe de taller':
            # Jefes de taller ven todos los diagnósticos, especialmente los sin asignar para completar
            diagnostics = Diagnostics.objects.all()
        elif user_role in ['Supervisor', 'Jefe de Flota']:
            # Supervisores y jefes ven todos los diagnósticos
            diagnostics = Diagnostics.objects.all()
        elif user_role == 'Recepcionista de Vehículos':
            # Recepcionistas ven diagnósticos que ellos crearon
            diagnostics = Diagnostics.objects.filter(diagnostics_created_by=request.user.flotauser)
        else:
            # Otros roles ven diagnósticos relacionados con sus incidentes, vehículo asignado, o creados por ellos
            diagnostics = Diagnostics.objects.filter(
                Q(incidents__reported_by=request.user.flotauser) |
                Q(diagnostics_created_by=request.user.flotauser) |
                Q(incidents__vehicle=request.user.flotauser.patent) if hasattr(request.user.flotauser, 'patent') and request.user.flotauser.patent else Q()
            )
    else:
        diagnostics = Diagnostics.objects.none()

    # Aplicar filtros si existen
    status_filter = request.GET.get('status')
    severity_filter = request.GET.get('severity')
    patent_filter = request.GET.get('patent')

    if status_filter:
        diagnostics = diagnostics.filter(status=status_filter)
    if severity_filter:
        diagnostics = diagnostics.filter(severity=severity_filter)
    if patent_filter:
        # Buscar en incidentes relacionados (tanto legacy como ManyToMany)
        diagnostics = diagnostics.filter(
            Q(incident__vehicle__patent__icontains=patent_filter) |
            Q(incidents__vehicle__patent__icontains=patent_filter)
        )

    diagnostics = diagnostics.select_related(
        'incident', 'incident__vehicle', 'incident__vehicle__type', 'assigned_to', 'incident__reported_by', 'diagnostics_created_by'
    ).prefetch_related(
        'incidents', 'incidents__vehicle', 'incidents__reported_by'
    ).order_by('-diagnostics_created_at').distinct()

    # Paginación
    paginator = Paginator(diagnostics, 12)  # 12 diagnósticos por página
    page = request.GET.get('page')

    try:
        diagnostics = paginator.page(page)
    except PageNotAnInteger:
        diagnostics = paginator.page(1)
    except EmptyPage:
        diagnostics = paginator.page(paginator.num_pages)

    # Agregar vehículos únicos a cada diagnóstico para evitar duplicados en el template
    for diagnostic in diagnostics:
        unique_vehicles = []
        seen_vehicles = set()
        
        # Agregar vehículos de incidentes ManyToMany
        for incident in diagnostic.incidents.all():
            if incident.vehicle.patent not in seen_vehicles:
                unique_vehicles.append(incident.vehicle)
                seen_vehicles.add(incident.vehicle.patent)
        
        # Agregar vehículo del incidente legacy si existe y no está ya incluido
        if diagnostic.incident and diagnostic.incident.vehicle.patent not in seen_vehicles:
            unique_vehicles.append(diagnostic.incident.vehicle)
        
        # Agregar el atributo unique_vehicles al diagnóstico
        diagnostic.unique_vehicles = unique_vehicles

    context = {
        'diagnostics': diagnostics,
        'status_choices': Diagnostics._meta.get_field('status').choices,
        'severity_choices': Diagnostics._meta.get_field('severity').choices,
    }

    return render(request, 'diagnostics/diagnostics_list.html', context)

@login_required
def diagnostics_detail(request, diagnostic_id):
    """Vista para ver el detalle de un diagnóstico"""
    diagnostic = get_object_or_404(
        Diagnostics.objects.select_related(
            'incident', 'incident__vehicle', 'assigned_to', 'created_by'
        ),
        id=diagnostic_id
    )

    # Verificar permisos según el rol del usuario
    if hasattr(request.user, 'flotauser'):
        user_role = request.user.flotauser.role.name
        can_view = (
            user_role in ['Supervisor', 'Jefe de Flota'] or
            diagnostic.assigned_to == request.user.flotauser or
            (diagnostic.incident and diagnostic.incident.reported_by == request.user.flotauser) or
            (diagnostic.incident and hasattr(request.user.flotauser, 'patent') and request.user.flotauser.patent == diagnostic.incident.vehicle)
        )
        if not can_view:
            messages.error(request, 'No tienes permisos para ver este diagnóstico.')
            return redirect('diagnostics:diagnostics_list')
    else:
        messages.error(request, 'Usuario no autorizado.')
        return redirect('login')

    context = {
        'diagnostic': diagnostic,
    }

    return render(request, 'diagnostics/diagnostics_detail.html', context)

@login_required
def diagnostics_create(request, incident_id=None):
    """Vista para crear un nuevo diagnóstico"""
    incident = None
    if incident_id:
        incident = get_object_or_404(Incident, id_incident=incident_id)

    if request.method == 'POST':
        form = DiagnosticsForm(request.POST, incident_id=incident_id, user=request.user)
        if form.is_valid():
            diagnostic = form.save(commit=False)

            # Si no hay mecánico asignado, asignar al usuario actual si es mecánico
            if not diagnostic.assigned_to and hasattr(request.user, 'flotauser'):
                if request.user.flotauser.role.name == 'Mecánico':
                    diagnostic.assigned_to = request.user.flotauser

            # Establecer el creador del diagnóstico
            if hasattr(request.user, 'flotauser'):
                diagnostic.diagnostics_created_by = request.user.flotauser

            diagnostic.save()
            # El método save del formulario ya maneja la relación ManyToMany con incidents
            messages.success(request, 'Diagnóstico creado exitosamente.')

            # Redirigir según el contexto
            return redirect('diagnostics:diagnostics_detail', diagnostic_id=diagnostic.id)
    else:
        # Crear formulario con incident_id para prepoblación
        initial_data = {}
        
        # Si no hay incident_id, es un diagnóstico in situ
        if not incident_id and hasattr(request.user, 'flotauser'):
            initial_data['status'] = 'Diagnostico_In_Situ'
        
        form = DiagnosticsForm(incident_id=incident_id, user=request.user, initial=initial_data)

    context = {
        'form': form,
        'incident': incident,  # Mantener para compatibilidad con template
        'incidents': [incident] if incident else [],  # Lista de incidentes para el template
        'is_create': True,
    }

    return render(request, 'diagnostics/diagnostics_form.html', context)

@login_required
def diagnostics_detail(request, diagnostic_id):
    """Vista para ver detalles de un diagnóstico"""
    diagnostic = get_object_or_404(
        Diagnostics.objects.select_related(
            'incident', 'incident__vehicle', 'assigned_to',
            'route', 'related_schedule', 'related_ingreso', 'related_work_order',
            'diagnostics_created_by'
        ).prefetch_related(
            'incidents', 'incidents__vehicle', 'incidents__reported_by'
        ),
        id=diagnostic_id
    )

    # Verificar permisos - diferentes reglas según el rol
    if hasattr(request.user, 'flotauser'):
        user_role = request.user.flotauser.role.name
        can_view = False

        if user_role in ['Supervisor', 'Jefe de Flota']:
            # Supervisores y jefes pueden ver todo
            can_view = True
        elif user_role == 'Jefe de taller':
            # Jefes de taller pueden ver todos los diagnósticos
            can_view = True
        elif user_role == 'Mecánico':
            # Mecánicos solo pueden ver diagnósticos asignados a ellos
            can_view = diagnostic.assigned_to == request.user.flotauser
        elif user_role == 'Recepcionista de Vehículos':
            # Recepcionistas pueden ver diagnósticos que crearon
            can_view = diagnostic.diagnostics_created_by == request.user.flotauser
        else:
            # Otros roles pueden ver diagnósticos relacionados con sus incidentes
            can_view = (
                (diagnostic.incident and diagnostic.incident.reported_by == request.user.flotauser) or
                any(incident.reported_by == request.user.flotauser for incident in diagnostic.incidents.all())
            )

        if not can_view:
            messages.error(request, 'No tienes permisos para ver este diagnóstico.')
            return redirect('diagnostics:diagnostics_list')

    # Obtener todos los incidentes relacionados
    incidents = []
    if diagnostic.incident:
        incidents.append(diagnostic.incident)
    incidents.extend(list(diagnostic.incidents.all()))

    context = {
        'diagnostic': diagnostic,
        'incidents': incidents,
    }

    return render(request, 'diagnostics/diagnostics_detail.html', context)

@login_required
def diagnostics_update(request, diagnostic_id):
    """Vista para actualizar un diagnóstico"""
    diagnostic = get_object_or_404(Diagnostics, id=diagnostic_id)

    # Verificar permisos - diferentes reglas según el rol
    if hasattr(request.user, 'flotauser'):
        user_role = request.user.flotauser.role.name
        can_edit = False

        if user_role in ['Supervisor', 'Jefe de Flota']:
            # Supervisores y jefes pueden editar todo
            can_edit = True
        elif user_role == 'Jefe de taller':
            # Jefes de taller pueden editar diagnósticos sin asignar o asignados
            can_edit = True
        elif user_role == 'Mecánico':
            # Mecánicos solo pueden editar diagnósticos asignados a ellos
            can_edit = diagnostic.assigned_to == request.user.flotauser
        elif user_role == 'Recepcionista de Vehículos':
            # Recepcionistas solo pueden editar diagnósticos que crearon y que estén en estado inicial
            can_edit = (diagnostic.diagnostics_created_by == request.user.flotauser and
                       diagnostic.status == 'Reportada')

        if not can_edit:
            messages.error(request, 'No tienes permisos para editar este diagnóstico.')
            return redirect('diagnostics:diagnostics_detail', diagnostic_id=diagnostic.id)

    if request.method == 'POST':
        form = DiagnosticsForm(request.POST, instance=diagnostic, user=request.user)
        if form.is_valid():
            diagnostic = form.save(commit=False)

            # Lógica de asignación según el rol
            if hasattr(request.user, 'flotauser'):
                user_role = request.user.flotauser.role.name
                if user_role == 'Jefe de taller' and not diagnostic.assigned_to:
                    # Jefe de taller puede asignar a un mecánico (viene del formulario)
                    pass  # El formulario ya maneja la asignación
                elif user_role == 'Mecánico' and not diagnostic.assigned_to:
                    # Si un mecánico edita un diagnóstico sin asignar, se lo asigna
                    diagnostic.assigned_to = request.user.flotauser

            # Establecer el usuario que actualizó el diagnóstico
            if hasattr(request.user, 'flotauser'):
                diagnostic.diagnostics_updated_by = request.user.flotauser

            diagnostic.save()
            messages.success(request, 'Diagnóstico actualizado exitosamente.')
            return redirect('diagnostics:diagnostics_detail', diagnostic_id=diagnostic.id)
    else:
        # Obtener incidentes relacionados para determinar el contexto
        incidents = []
        if diagnostic.incident:
            incidents.append(diagnostic.incident)
        incidents.extend(list(diagnostic.incidents.all()))
        
        # Determinar si es diagnóstico in situ (sin incidentes asociados)
        is_in_situ = len(incidents) == 0
        
        # También considerar "in situ" cuando un jefe de taller edita un diagnóstico 
        # creado por recepcionista que está en blanco (estado Reportada)
        is_blank_card_from_recepcionista = (
            hasattr(request.user, 'flotauser') and 
            request.user.flotauser.role.name == 'Jefe de taller' and
            diagnostic.diagnostics_created_by and
            diagnostic.diagnostics_created_by.role.name == 'Recepcionista de Vehículos' and
            diagnostic.status == 'Reportada' and
            len(incidents) > 0  # Tiene incidentes asociados
        )
        
        # Usar lógica in situ si cumple cualquiera de las condiciones
        should_prepopulate_in_situ = is_in_situ or is_blank_card_from_recepcionista
        
        # Preparar datos iniciales
        initial_data = {}
        
        # Pre-poblar estado para diagnósticos in situ o tarjetas en blanco de recepcionista
        if should_prepopulate_in_situ and (not diagnostic.status or is_blank_card_from_recepcionista):
            initial_data['status'] = 'Diagnostico_In_Situ'
        
        # Pre-poblar ruta desde el vehículo del primer incidente o del creador (para in situ)
        if not diagnostic.route:
            vehicle = None
            
            if incidents:
                # Si hay incidentes, usar el vehículo del primer incidente
                vehicle = incidents[0].vehicle
            elif should_prepopulate_in_situ and diagnostic.diagnostics_created_by:
                # Si es in situ o tarjeta en blanco, usar el vehículo asignado al creador
                vehicle = diagnostic.diagnostics_created_by.patent
            
            if vehicle:
                # Usar la ruta activa del vehículo
                active_route = vehicle.active_route
                if active_route:
                    initial_data['route'] = active_route
        
        form = DiagnosticsForm(instance=diagnostic, user=request.user, initial=initial_data)

    # Obtener vehículos únicos de los incidentes
    unique_vehicles = []
    seen_vehicles = set()
    for incident in incidents:
        if incident.vehicle.patent not in seen_vehicles:
            unique_vehicles.append(incident.vehicle)
            seen_vehicles.add(incident.vehicle.patent)

    context = {
        'form': form,
        'diagnostic': diagnostic,
        'incidents': incidents,
        'unique_vehicles': unique_vehicles,
        'is_create': False,
    }

    return render(request, 'diagnostics/diagnostics_form.html', context)


@login_required
def get_incident_vehicle_info(request, incident_id):
    """API endpoint para obtener información del vehículo de un incidente"""
    try:
        incident = Incident.objects.select_related('vehicle__type', 'vehicle__status').get(id_incident=incident_id)

        vehicle_data = {
            'patent': incident.vehicle.patent,
            'brand': incident.vehicle.brand,
            'model': incident.vehicle.model,
            'year': incident.vehicle.year,
            'type_name': incident.vehicle.type.name if incident.vehicle.type else None,
            'mileage': incident.vehicle.mileage,
            'status_name': incident.vehicle.status.name if incident.vehicle.status else None,
        }

        return JsonResponse({
            'success': True,
            'vehicle': vehicle_data
        })

    except Incident.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Incidente no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def diagnostics_create_multiple(request):
    """Vista para crear un diagnóstico que abarque múltiples incidentes"""
    incident_ids_str = request.GET.get('incidents', '')
    incident_ids = [int(id.strip()) for id in incident_ids_str.split(',') if id.strip()] if incident_ids_str else []

    if not incident_ids:
        messages.error(request, 'No se especificaron incidentes.')
        return redirect('incidents:incident_list')

    # Obtener los incidentes
    incidents = Incident.objects.filter(id_incident__in=incident_ids).select_related('vehicle')

    if len(incidents) != len(incident_ids):
        messages.error(request, 'Algunos incidentes no existen.')
        return redirect('incidents:incident_list')

    # Verificar que todos los incidentes pertenezcan al mismo vehículo
    vehicle_ids = incidents.values_list('vehicle_id', flat=True).distinct()
    if len(vehicle_ids) > 1:
        messages.error(request, 'Los incidentes seleccionados deben pertenecer al mismo vehículo.')
        return redirect('incidents:incident_list')

    vehicle = incidents[0].vehicle

    if request.method == 'POST':
        form = DiagnosticsForm(request.POST)
        if form.is_valid():
            diagnostic = form.save(commit=False)

            # Si no hay mecánico asignado, asignar al usuario actual si es mecánico
            if not diagnostic.assigned_to and hasattr(request.user, 'flotauser'):
                if request.user.flotauser.role.name == 'Mecánico':
                    diagnostic.assigned_to = request.user.flotauser

            # Establecer el creador del diagnóstico
            if hasattr(request.user, 'flotauser'):
                diagnostic.diagnostics_created_by = request.user.flotauser

            diagnostic.save()
            # Asignar los incidentes al diagnóstico
            form.save_m2m()  # Esto maneja la relación ManyToMany

            messages.success(request, f'Diagnóstico creado exitosamente para {len(incidents)} incidente(s) del vehículo {vehicle.patent}.')
            return redirect('diagnostics:diagnostics_detail', diagnostic_id=diagnostic.id)
    else:
        # Crear formulario prepoblado con los incidentes
        form = DiagnosticsForm(initial={'incidents': incidents})

    context = {
        'form': form,
        'incidents': incidents,
        'vehicle': vehicle,
        'is_create': True,
        'is_multiple': True,
    }

    return render(request, 'diagnostics/diagnostics_form.html', context)
