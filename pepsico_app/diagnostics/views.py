from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from documents.models import Diagnostics, Incident, Vehicle, FlotaUser, Route, WorkOrder, WorkOrderStatus
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
            # Recepcionistas ven diagnósticos que ellos crearon Y diagnósticos trabajados por otros roles
            diagnostics = Diagnostics.objects.filter(
                Q(diagnostics_created_by=request.user.flotauser) |  # Diagnósticos que creó
                Q(status__in=['Diagnostico_In_Situ', 'OT_Generada', 'Resuelta'])  # Diagnósticos trabajados por otros
            )
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
        
        # Determinar el estado de completitud basado en actores
        # Jefe de taller asignó mecánico Y mecánico completó el diagnóstico
        if diagnostic.assigned_to and (diagnostic.diagnostic_completed_at or diagnostic.diagnostic_by):
            diagnostic.completion_status = 'completed'
            diagnostic.completion_text = 'Diagnóstico Completado - Continuar a OT'
        elif diagnostic.assigned_to:
            diagnostic.completion_status = 'pending_completion'
            diagnostic.completion_text = 'Pendiente - Completar Diagnóstico'
        else:
            diagnostic.completion_status = 'pending_assignment'
            diagnostic.completion_text = 'Pendiente - Asignar Mecánico'

    context = {
        'diagnostics': diagnostics,
        'status_choices': Diagnostics._meta.get_field('status').choices,
        'severity_choices': Diagnostics._meta.get_field('severity').choices,
    }

    return render(request, 'diagnostics/diagnostics_list.html', context)

@login_required
def diagnostics_create(request, incident_id=None):
    """Vista para crear un nuevo diagnóstico"""
    incident = None
    if incident_id:
        incident = get_object_or_404(Incident, id_incident=incident_id)

    # Verificar si viene desde un ingreso (diagnóstico en blanco)
    from_ingreso_id = request.GET.get('from_ingreso')
    auto_create = request.GET.get('auto_create') == 'true'
    ingreso = None
    if from_ingreso_id:
        from documents.models import Ingreso
        ingreso = get_object_or_404(Ingreso, id_ingreso=from_ingreso_id)

    # Si es auto-creación desde ingreso, crear automáticamente
    if auto_create and from_ingreso_id and ingreso and request.method == 'POST':
        # Validar que el ingreso tenga ingreso técnico completado
        if not ingreso.es_ingreso_tecnico:
            messages.error(request, 'Primero realizar ingreso técnico antes de hacer diagnóstico')
            return redirect('agenda:ingreso_detail', ingreso_id=ingreso.id_ingreso)
        
        # Obtener la ruta activa del vehículo del ingreso
        route = None
        if ingreso.patent and hasattr(ingreso.patent, 'active_route'):
            route = ingreso.patent.active_route
        
        # Crear diagnóstico automáticamente con datos básicos
        diagnostic = Diagnostics.objects.create(
            severity=request.POST.get('severity', 'Sin especificar'),
            category=request.POST.get('category', 'Mantenimiento'),
            symptoms=request.POST.get('symptoms', 'Diagnóstico inicial del ingreso técnico'),
            location=request.POST.get('location', f'Ingreso Técnico - Vehículo {ingreso.patent}'),
            status='Reportada',
            route=route,  # Asociar la ruta del vehículo del ingreso
            diagnostics_created_by=request.user.flotauser if hasattr(request.user, 'flotauser') else None,
            related_ingreso=ingreso
        )
        
        messages.success(request, f'Diagnóstico creado exitosamente para el ingreso {ingreso.id_ingreso}.')
        return redirect('diagnostics:diagnostics_list')

    if request.method == 'POST':
        # Validar que si viene desde un ingreso, tenga ingreso técnico completado
        if ingreso and not ingreso.es_ingreso_tecnico:
            messages.error(request, 'Primero realizar ingreso técnico antes de hacer diagnóstico')
            return redirect('agenda:ingreso_detail', ingreso_id=ingreso.id_ingreso)
        
        form = DiagnosticsForm(request.POST, incident_id=incident_id, user=request.user)
        if form.is_valid():
            diagnostic = form.save(commit=False)

            # Validar lógica de estado e incidentes
            selected_status = form.cleaned_data.get('status')
            selected_incidents = form.cleaned_data.get('incidents', [])
            
            # Para diagnósticos reportados: requieren incidentes asociados O estar relacionados con un ingreso
            if selected_status == 'Reportada' and not selected_incidents and not ingreso:
                form.add_error('incidents', 'Los diagnósticos reportados deben estar asociados a al menos un incidente o relacionados con un ingreso técnico.')
            elif selected_status == 'Diagnostico_In_Situ' and selected_incidents:
                form.add_error('incidents', 'Los diagnósticos in situ no deben estar asociados a incidentes.')
            
            # Si hay errores de validación, volver a renderizar el formulario
            if form.errors:
                # Si hay errores de validación, volver a renderizar el formulario
                context = {
                    'form': form,
                    'incident': incident,
                    'incidents': [incident] if incident else [],
                    'ingreso': ingreso,
                    'is_create': True,
                    'from_ingreso': bool(from_ingreso_id),
                }
                return render(request, 'diagnostics/diagnostics_form.html', context)

            # Si no hay mecánico asignado, asignar al usuario actual si es mecánico
            if not diagnostic.assigned_to and hasattr(request.user, 'flotauser'):
                if request.user.flotauser.role.name == 'Mecánico':
                    diagnostic.assigned_to = request.user.flotauser

            # Establecer el creador del diagnóstico
            if hasattr(request.user, 'flotauser'):
                diagnostic.diagnostics_created_by = request.user.flotauser

            # Si viene desde un ingreso, relacionarlo
            if ingreso:
                diagnostic.related_ingreso = ingreso

            diagnostic.save()
            # El método save del formulario ya maneja la relación ManyToMany con incidents
            messages.success(request, 'Diagnóstico creado exitosamente.')

            # Redirigir según el contexto
            return redirect('diagnostics:diagnostics_detail', diagnostic_id=diagnostic.id)
    else:
        # Crear formulario con incident_id para prepoblación
        initial_data = {}
        
        # No forzar estado inicial - permitir que el mecánico elija
        # Si viene desde un ingreso, sugerir Reportada pero permitir cambio
        if from_ingreso_id and ingreso:
            initial_data['status'] = 'Reportada'
            # Pre-poblar con información del ingreso
            if hasattr(request.user, 'flotauser'):
                initial_data['location'] = f'Ingreso Técnico - Vehículo {ingreso.patent}'
        # Para otros casos, no establecer estado inicial por defecto
        
        form = DiagnosticsForm(incident_id=incident_id, user=request.user, initial=initial_data)

    context = {
        'form': form,
        'incident': incident,  # Mantener para compatibilidad con template
        'incidents': [incident] if incident else [],  # Lista de incidentes para el template
        'ingreso': ingreso,  # Agregar el ingreso si existe
        'is_create': True,
        'from_ingreso': bool(from_ingreso_id),  # Indicar si viene de ingreso
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
            # Recepcionistas pueden ver diagnósticos que crearon O diagnósticos trabajados por otros
            can_view = (
                diagnostic.diagnostics_created_by == request.user.flotauser or  # Creó el diagnóstico
                diagnostic.status in ['Diagnostico_In_Situ', 'OT_Generada', 'Resuelta']  # Puede ver diagnósticos trabajados
            )
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

    # Determinar el estado de completitud basado en actores
    # Jefe de taller asignó mecánico Y mecánico completó el diagnóstico
    if diagnostic.assigned_to and (diagnostic.diagnostic_completed_at or diagnostic.diagnostic_by):
        diagnostic.completion_status = 'completed'
        diagnostic.completion_text = 'Diagnóstico Completado - Continuar a OT'
    elif diagnostic.assigned_to:
        diagnostic.completion_status = 'pending_completion'
        diagnostic.completion_text = 'Pendiente - Completar Diagnóstico'
    else:
        diagnostic.completion_status = 'pending_assignment'
        diagnostic.completion_text = 'Pendiente - Asignar Mecánico'

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
            # Validar lógica de estado e incidentes antes de guardar
            selected_status = form.cleaned_data.get('status')
            selected_incidents = form.cleaned_data.get('incidents', [])
            
            # Para diagnósticos reportados: requieren incidentes asociados O estar relacionados con un ingreso
            if selected_status == 'Reportada' and not selected_incidents and not diagnostic.related_ingreso:
                form.add_error('incidents', 'Los diagnósticos reportados deben estar asociados a al menos un incidente o relacionados con un ingreso técnico.')
            elif selected_status == 'Diagnostico_In_Situ' and selected_incidents:
                form.add_error('incidents', 'Los diagnósticos in situ no deben estar asociados a incidentes.')
            
            # Si hay errores de validación, volver a renderizar el formulario
            if form.errors:
                # Obtener incidentes relacionados para el contexto
                incidents = []
                if diagnostic.incident:
                    incidents.append(diagnostic.incident)
                incidents.extend(list(diagnostic.incidents.all()))
                
                # Obtener vehículos únicos
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

            diagnostic = form.save(commit=False)

            # Lógica de asignación según el rol
            if hasattr(request.user, 'flotauser'):
                user_role = request.user.flotauser.role.name
                if user_role == 'Jefe de taller' and not diagnostic.assigned_to:
                    # Jefe de taller puede asignar a un mecánico (viene del formulario)
                    pass  # El formulario ya maneja la asignación
                elif user_role == 'Mecánico':
                    # Si un mecánico edita un diagnóstico, se lo asigna si no está asignado
                    if not diagnostic.assigned_to:
                        diagnostic.assigned_to = request.user.flotauser
                    # Marcar como quien realizó el diagnóstico si no está marcado
                    if not diagnostic.diagnostic_by:
                        diagnostic.diagnostic_by = request.user.flotauser
                    # NO cambiar automáticamente el estado - permitir que el mecánico elija

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
        
        # Preparar datos iniciales
        initial_data = {}

        # Para edición: mantener el estado actual, no forzar basado en incidentes
        # Solo establecer estado por defecto si no tiene ninguno
        if not diagnostic.status:
            initial_data['status'] = 'Reportada'        # Pre-poblar ruta desde el vehículo del primer incidente o del creador (para in situ)
        if not diagnostic.route:
            vehicle = None
            
            if incidents:
                # Si hay incidentes, usar el vehículo del primer incidente
                vehicle = incidents[0].vehicle
            elif is_in_situ:
                # Si es in situ, primero intentar usar el vehículo del ingreso relacionado
                if diagnostic.related_ingreso:
                    vehicle = diagnostic.related_ingreso.patent
                # Si no hay ingreso relacionado, usar el vehículo asignado al creador
                elif diagnostic.diagnostics_created_by:
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
    
    # Si no hay incidentes pero hay related_ingreso, incluir el vehículo del ingreso
    if not incidents and diagnostic.related_ingreso:
        vehicle = diagnostic.related_ingreso.patent
        if vehicle.patent not in seen_vehicles:
            unique_vehicles.append(vehicle)
            seen_vehicles.add(vehicle.patent)

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


@login_required
@require_POST
def generate_work_order_from_diagnostic(request, diagnostic_id):
    """Vista para generar una orden de trabajo desde un diagnóstico"""
    diagnostic = get_object_or_404(Diagnostics, id=diagnostic_id)

    # Verificar que no exista ya una orden de trabajo para este diagnóstico
    if diagnostic.related_work_order:
        return JsonResponse({
            'success': False,
            'error': 'Ya existe una orden de trabajo para este diagnóstico.'
        }, status=400)

    try:
        # Obtener o crear el estado por defecto
        default_status = WorkOrderStatus.objects.filter(name='Pendiente').first()
        if not default_status:
            default_status = WorkOrderStatus.objects.create(
                name='Pendiente',
                description='Orden de trabajo creada, pendiente de asignación',
                color='#ffc107'
            )

        # Crear la orden de trabajo
        observations = f"Orden de trabajo generada desde diagnóstico #{diagnostic.id}"
        if diagnostic.related_ingreso:
            observations += f" (relacionado con ingreso #{diagnostic.related_ingreso.id_ingreso})"

        work_order = WorkOrder.objects.create(
            ingreso=diagnostic.related_ingreso if diagnostic.related_ingreso else None,
            observations=observations,
            status=default_status,
            created_by=request.user.flotauser if hasattr(request.user, 'flotauser') else None,
        )

        # Actualizar el diagnóstico
        diagnostic.related_work_order = work_order
        diagnostic.status = 'OT_Generada'
        diagnostic.save()

        return JsonResponse({
            'success': True,
            'message': f'Orden de trabajo OT-{work_order.id_work_order} generada exitosamente.',
            'work_order_id': work_order.id_work_order
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({
            'success': False,
            'error': f'Error al generar la orden de trabajo: {str(e)}',
            'details': error_details
        }, status=500)
