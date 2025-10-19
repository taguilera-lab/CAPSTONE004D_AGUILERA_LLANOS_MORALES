from django.shortcuts import render, get_object_or_404, redirect
from documents.models import Ingreso, MaintenanceSchedule, Vehicle, Route
from .forms import IngresoForm, AgendarIngresoForm
import json

def calendario(request):
    schedules = MaintenanceSchedule.objects.all()
    events = []
    for schedule in schedules:
        events.append({
            'id': schedule.id_schedule,
            'title': f"{schedule.patent} - {schedule.service_type.name if schedule.service_type else 'Servicio por definir'}",
            'start': schedule.start_datetime.isoformat(),
            'end': schedule.end_datetime.isoformat() if schedule.end_datetime else None,
            'description': schedule.observations or '',
            'patent': str(schedule.patent),
            'service_type': schedule.service_type.name if schedule.service_type else '',
            'recurrence_rule': schedule.recurrence_rule or '',
            'reminder_minutes': schedule.reminder_minutes or 0,
            'assigned_user': schedule.assigned_user.name if schedule.assigned_user else '',
            'supervisor': schedule.supervisor.name if schedule.supervisor else '',
            'status': schedule.status.name if schedule.status else '',
        })
    return render(request, 'agenda/calendario.html', {'events': json.dumps(events)})

def ingresos_list(request):
    ingresos = Ingreso.objects.all()
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
    ).select_related('patent', 'service_type').order_by('start_datetime')
    
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
            if hasattr(request, 'user') and request.user.is_authenticated:
                ingreso.entry_registered_by = request.user
            
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
            # ingreso.exit_registered_by = request.user  # Ajustar según auth
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


def agendar_ingreso(request):
    vehicles = list(Vehicle.objects.values('patent', 'site__name'))
    routes = list(Route.objects.values('id_route', 'route_code', 'truck'))
    if request.method == 'POST':
        form = AgendarIngresoForm(request.POST, user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None)
        if form.is_valid():
            schedule = form.save(commit=False)
            
            # Forzar que el chofer esperado sea siempre el usuario logueado
            if hasattr(request, 'user') and request.user.is_authenticated:
                schedule.expected_chofer = request.user
            
            schedule.save()
            return redirect('calendario')
    else:
        # Pre-llenar el chofer con el usuario actual si está disponible
        form = AgendarIngresoForm(user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None)
    
    return render(request, 'agenda/agendar_ingreso.html', {'form': form})
