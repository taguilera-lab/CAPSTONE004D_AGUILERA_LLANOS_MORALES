from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from documents.models import Diagnostics, Incident, Vehicle, FlotaUser
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
        elif user_role in ['Supervisor', 'Jefe de Flota']:
            # Supervisores y jefes ven todos los diagnósticos
            diagnostics = Diagnostics.objects.all()
        else:
            # Otros roles ven diagnósticos relacionados con sus incidentes, vehículo asignado, o creados por ellos
            query_parts = [
                Q(incident__reported_by=request.user.flotauser),
                Q(diagnostics_created_by=request.user.flotauser)  # Incluir diagnósticos creados por el usuario
            ]
            if hasattr(request.user.flotauser, 'patent') and request.user.flotauser.patent:
                query_parts.append(Q(incident__vehicle=request.user.flotauser.patent))
            diagnostics = Diagnostics.objects.filter(*query_parts)
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
        diagnostics = diagnostics.filter(incident__vehicle__patent__icontains=patent_filter)

    diagnostics = diagnostics.select_related(
        'incident', 'incident__vehicle', 'incident__vehicle__type', 'assigned_to', 'incident__reported_by'
    ).order_by('-incident__reported_at')

    # Paginación
    paginator = Paginator(diagnostics, 12)  # 12 diagnósticos por página
    page = request.GET.get('page')

    try:
        diagnostics = paginator.page(page)
    except PageNotAnInteger:
        diagnostics = paginator.page(1)
    except EmptyPage:
        diagnostics = paginator.page(paginator.num_pages)

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
        form = DiagnosticsForm(request.POST)
        if form.is_valid():
            diagnostic = form.save(commit=False)

            # Si se especificó un incidente, asociarlo
            if incident:
                diagnostic.incident = incident

            # Si no hay mecánico asignado, asignar al usuario actual si es mecánico
            if not diagnostic.assigned_to and hasattr(request.user, 'flotauser'):
                if request.user.flotauser.role.name == 'Mecánico':
                    diagnostic.assigned_to = request.user.flotauser

            # Establecer el creador del diagnóstico
            if hasattr(request.user, 'flotauser'):
                diagnostic.diagnostics_created_by = request.user.flotauser

            diagnostic.save()
            messages.success(request, 'Diagnóstico creado exitosamente.')

            # Redirigir según el contexto
            if incident:
                return redirect('diagnostics:diagnostics_detail', diagnostic_id=diagnostic.id)
            else:
                return redirect('diagnostics:diagnostics_list')
    else:
        # Pre-llenar formulario si hay incidente
        initial_data = {}
        if incident:
            initial_data = {
                'incident': incident,
                'severity': 'Media',  # Valor por defecto
                'status': 'Diagnostico_In_Situ',
            }
        form = DiagnosticsForm(initial=initial_data)

    context = {
        'form': form,
        'incident': incident,
        'is_create': True,
    }

    return render(request, 'diagnostics/diagnostics_form.html', context)

@login_required
def diagnostics_detail(request, diagnostic_id):
    """Vista para ver detalles de un diagnóstico"""
    diagnostic = get_object_or_404(
        Diagnostics.objects.select_related(
            'incident', 'incident__vehicle', 'assigned_to',
            'route', 'related_schedule', 'related_ingreso', 'related_work_order'
        ),
        id=diagnostic_id
    )

    # Verificar permisos - usuarios solo pueden ver diagnósticos relacionados con ellos
    if hasattr(request.user, 'flotauser'):
        user_role = request.user.flotauser.role.name
        can_view = (
            user_role in ['Supervisor', 'Jefe de Flota'] or
            diagnostic.assigned_to == request.user.flotauser or
            (diagnostic.incident and diagnostic.incident.reported_by == request.user.flotauser)
        )
        if not can_view:
            messages.error(request, 'No tienes permisos para ver este diagnóstico.')
            return redirect('diagnostics:diagnostics_list')

    context = {
        'diagnostic': diagnostic,
    }

    return render(request, 'diagnostics/diagnostics_detail.html', context)

@login_required
def diagnostics_update(request, diagnostic_id):
    """Vista para actualizar un diagnóstico"""
    diagnostic = get_object_or_404(Diagnostics, id=diagnostic_id)

    # Verificar permisos - solo mecánicos asignados o supervisores pueden editar
    if hasattr(request.user, 'flotauser'):
        user_role = request.user.flotauser.role.name
        can_edit = (
            user_role in ['Supervisor', 'Jefe de Flota'] or
            diagnostic.assigned_to == request.user.flotauser
        )
        if not can_edit:
            messages.error(request, 'No tienes permisos para editar este diagnóstico.')
            return redirect('diagnostics:diagnostics_detail', diagnostic_id=diagnostic.id)

    if request.method == 'POST':
        form = DiagnosticsForm(request.POST, instance=diagnostic)
        if form.is_valid():
            diagnostic = form.save(commit=False)
            # Establecer el usuario que actualizó el diagnóstico
            if hasattr(request.user, 'flotauser'):
                diagnostic.diagnostics_updated_by = request.user.flotauser
            diagnostic.save()
            messages.success(request, 'Diagnóstico actualizado exitosamente.')
            return redirect('diagnostics:diagnostics_detail', diagnostic_id=diagnostic.id)
    else:
        form = DiagnosticsForm(instance=diagnostic)

    context = {
        'form': form,
        'diagnostic': diagnostic,
        'incident': diagnostic.incident,
        'is_create': False,
    }

    return render(request, 'diagnostics/diagnostics_form.html', context)
