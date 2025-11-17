from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .forms import LoginForm
from documents.models import FlotaUser

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido, {username}!")
                # Redirigir según rol
                try:
                    flota_user = user.flotauser
                    role_name = flota_user.role.name
                    if role_name == 'Jefe de Flota':
                        return redirect('supervisor_dashboard')
                    elif role_name == 'Mecánico':
                        return redirect('mecanico_dashboard')
                    elif role_name == 'Vendedor':
                        return redirect('vendedor_dashboard')
                    elif role_name == 'Guardia':
                        return redirect('guardia_dashboard')
                    elif role_name == 'Bodeguero':
                        return redirect('bodeguero_dashboard')
                    elif role_name == 'Supervisor':
                        return redirect('supervisor_dashboard')
                    elif role_name == 'Jefe de taller':
                        return redirect('jefe_taller_dashboard')
                    elif role_name == 'Recepcionista de Vehículos':
                        return redirect('recepcionista_vehiculos_dashboard')
                    else:
                        return redirect('home')
                except FlotaUser.DoesNotExist:
                    messages.error(request, "Usuario no tiene perfil de FlotaUser.")
                    return redirect('login')
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Formulario inválido.")
    else:
        form = LoginForm()
    return render(request, 'login/login.html', {'form': form})

@login_required
def user_dashboard(request):
    """Redirige al dashboard correspondiente según el rol del usuario"""
    try:
        flota_user = request.user.flotauser
        role_name = flota_user.role.name
        if role_name == 'Jefe de Flota':
            return redirect('jefe_flota_dashboard')
        elif role_name == 'Mecánico':
            return redirect('mecanico_dashboard')
        elif role_name == 'Vendedor':
            return redirect('vendedor_dashboard')
        elif role_name == 'Guardia':
            return redirect('guardia_dashboard')
        elif role_name == 'Bodeguero':
            return redirect('bodeguero_dashboard')
        elif role_name == 'Supervisor':
            return redirect('supervisor_dashboard')
        elif role_name == 'Jefe de taller':
            return redirect('jefe_taller_dashboard')
        elif role_name == 'Recepcionista de Vehículos':
            return redirect('recepcionista_dashboard')
        else:
            return redirect('busqueda_patente')  # fallback
    except FlotaUser.DoesNotExist:
        return redirect('busqueda_patente')  # fallback

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect('login')

# Dashboards placeholders (redirigir a vistas reales)
@login_required
def jefe_flota_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Jefe de Flota'})

@login_required
def mecanico_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Mecánico'})

@login_required
def vendedor_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Vendedor'})

@login_required
def guardia_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Guardia'})

@login_required
def bodeguero_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Bodeguero'})

@login_required
def supervisor_dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Q, Sum, Avg
    from documents.models import WorkOrder, Ingreso, FlotaUser, Role, ServiceType
    from document_upload.models import UploadedDocument, DocumentType

    now = timezone.now()
    last_month = now - timedelta(days=30)

    # KPI 1: Órdenes de trabajo activas
    active_work_orders = WorkOrder.objects.filter(
        ~Q(status__name__icontains='completado') &
        ~Q(status__name__icontains='cerrado')
    ).count()

    # KPI 2: Vehículos actualmente en taller (ingresos sin fecha de salida)
    vehicles_in_workshop = Ingreso.objects.filter(
        exit_datetime__isnull=True
    ).count()

    # KPI 3: Documentos subidos en el último mes
    documents_last_month = UploadedDocument.objects.filter(
        uploaded_at__gte=last_month
    ).count()

    # KPI 4: Órdenes de trabajo completadas en el último mes
    completed_work_orders_last_month = WorkOrder.objects.filter(
        actual_completion__gte=last_month,
        status__name__icontains='completado'
    ).count()

    # KPI 5: Total de usuarios activos (solo jefe de flota y supervisor)
    active_supervisor_users = FlotaUser.objects.filter(
        role__name__in=['Jefe de Flota', 'Supervisor'],
        status__name__icontains='activo'
    ).count()

    # KPI 6: Productividad promedio (órdenes completadas vs total creadas en el último mes)
    total_work_orders_last_month = WorkOrder.objects.filter(
        created_datetime__gte=last_month
    ).count()

    productivity_ratio = 0
    if total_work_orders_last_month > 0:
        productivity_ratio = (completed_work_orders_last_month / total_work_orders_last_month) * 100

    # KPI 7: Horas hombre trabajadas en el último mes
    total_man_hours_last_month = WorkOrder.objects.filter(
        created_datetime__gte=last_month
    ).aggregate(
        total_hours=Sum('mechanic_assignments__hours_worked')
    )['total_hours'] or 0

    # ===== DATOS PARA GRÁFICOS =====

    # Gráfico de barras: Órdenes de trabajo por estado
    work_orders_by_status = WorkOrder.objects.values('status__name').annotate(
        count=Count('id_work_order')
    ).order_by('-count')[:10]

    status_labels = [item['status__name'] or 'Sin estado' for item in work_orders_by_status]
    status_counts = [item['count'] for item in work_orders_by_status]

    # Gráfico circular: Tipos de servicio más comunes
    service_types_data = WorkOrder.objects.values('service_type__name').annotate(
        count=Count('id_work_order')
    ).exclude(service_type__name__isnull=True).order_by('-count')[:8]

    service_labels = [item['service_type__name'] for item in service_types_data]
    service_counts = [item['count'] for item in service_types_data]

    # Gráfico de líneas: Tendencia de órdenes de trabajo (últimos 6 meses)
    monthly_trend = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        completed_count = WorkOrder.objects.filter(
            actual_completion__gte=month_start,
            actual_completion__lte=month_end,
            status__name__icontains='completado'
        ).count()

        monthly_trend.append({
            'month': month_start.strftime('%b %Y'),
            'completed': completed_count
        })

    trend_labels = [item['month'] for item in monthly_trend]
    trend_completed = [item['completed'] for item in monthly_trend]

    # Gráfico de barras: Documentos por tipo
    documents_by_type = UploadedDocument.objects.values('document_type__name').annotate(
        count=Count('id_document')
    ).exclude(document_type__name__isnull=True).order_by('-count')[:6]

    doc_type_labels = [item['document_type__name'] for item in documents_by_type]
    doc_type_counts = [item['count'] for item in documents_by_type]

    context = {
        'role': 'Supervisor',
        'kpis': {
            'active_work_orders': active_work_orders,
            'vehicles_in_workshop': vehicles_in_workshop,
            'documents_last_month': documents_last_month,
            'completed_work_orders_last_month': completed_work_orders_last_month,
            'active_supervisor_users': active_supervisor_users,
            'productivity_ratio': round(productivity_ratio, 1),
            'total_man_hours_last_month': round(total_man_hours_last_month, 1),
        },
        'charts': {
            'status_labels': status_labels,
            'status_counts': status_counts,
            'service_labels': service_labels,
            'service_counts': service_counts,
            'trend_labels': trend_labels,
            'trend_completed': trend_completed,
            'doc_type_labels': doc_type_labels,
            'doc_type_counts': doc_type_counts,
        }
    }

    return render(request, 'login/dashboard.html', context)

@login_required
def jefe_taller_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Jefe de taller'})

@login_required
def jefe_taller_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Jefe de taller'})

@login_required
def recepcionista_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Recepcionista de Vehículos'})

@login_required
def vendedor_dashboard(request):
    """Dashboard para Vendedor - Agenda e Incidentes"""
    from django.utils import timezone
    from documents.models import Incident, MaintenanceSchedule

    now = timezone.now()
    today = now.date()

    # Incidentes reportados hoy
    incidents_today = Incident.objects.filter(
        created_at__date=today
    ).count()

    # Incidentes pendientes (sin diagnóstico resuelto)
    from documents.models import Diagnostics
    thirty_days_ago = now - timezone.timedelta(days=30)
    pending_incidents = Incident.objects.filter(
        reported_at__gte=thirty_days_ago
    ).exclude(
        diagnostics__status='Resuelta'
    ).count()

    # Agendamientos para hoy
    schedules_today = MaintenanceSchedule.objects.filter(
        start_datetime__date=today
    ).count()

    # Agendamientos pendientes
    pending_schedules = MaintenanceSchedule.objects.filter(
        start_datetime__date__gte=today,
        status__name__icontains='programado'
    ).count()

    context = {
        'role': 'Vendedor',
        'features': {
            'incidents_today': incidents_today,
            'pending_incidents': pending_incidents,
            'schedules_today': schedules_today,
            'pending_schedules': pending_schedules,
        }
    }

    return render(request, 'login/dashboard_vendedor.html', context)

@login_required
def guardia_dashboard(request):
    """Dashboard para Guardia - Ingresos e Incidentes"""
    from django.utils import timezone
    from documents.models import Ingreso, Incident

    now = timezone.now()
    today = now.date()

    # Vehículos ingresados hoy
    ingresos_today = Ingreso.objects.filter(
        entry_datetime__date=today
    ).count()

    # Vehículos actualmente en taller
    vehicles_in_workshop = Ingreso.objects.filter(
        exit_datetime__isnull=True
    ).count()

    # Incidentes reportados por guardia hoy
    incidents_today = Incident.objects.filter(
        created_at__date=today,
        reported_by__role__name__icontains='guardia'
    ).count()

    # Incidentes críticos pendientes (sin diagnóstico resuelto)
    critical_incidents = Incident.objects.filter(
        priority='Critica'
    ).exclude(
        diagnostics__status='Resuelta'
    ).count()

    context = {
        'role': 'Guardia',
        'features': {
            'ingresos_today': ingresos_today,
            'vehicles_in_workshop': vehicles_in_workshop,
            'incidents_today': incidents_today,
            'critical_incidents': critical_incidents,
        }
    }

    return render(request, 'login/dashboard_guardia.html', context)

@login_required
def bodeguero_dashboard(request):
    """Dashboard para Bodeguero - Repuestos"""
    from repuestos.models import SparePartStock, StockMovement

    # Total de repuestos en inventario
    total_parts = SparePartStock.objects.count()

    # Repuestos con stock bajo
    low_stock_parts = SparePartStock.objects.filter(
        current_stock__lte=5
    ).count()

    # Movimientos de hoy
    from django.utils import timezone
    today = timezone.now().date()
    movements_today = StockMovement.objects.filter(
        performed_at__date=today
    ).count()

    # Valor total del inventario
    total_inventory_value = SparePartStock.objects.aggregate(
        total_value=Sum('current_stock')
    )['total_value'] or 0

    context = {
        'role': 'Bodeguero',
        'features': {
            'total_parts': total_parts,
            'low_stock_parts': low_stock_parts,
            'movements_today': movements_today,
            'total_inventory_value': total_inventory_value,
        }
    }

    return render(request, 'login/dashboard_bodeguero.html', context)

@login_required
def mecanico_dashboard(request):
    """Dashboard para Mecánico - Diagnósticos y Órdenes de Trabajo"""
    from documents.models import WorkOrder, Diagnostics
    from django.utils import timezone

    now = timezone.now()
    today = now.date()

    # Órdenes de trabajo asignadas al mecánico
    user_work_orders = WorkOrder.objects.filter(
        mechanic_assignments__mechanic__user=request.user
    ).distinct()

    # OT activas
    active_work_orders = user_work_orders.filter(
        status__name__icontains='en progreso'
    ).count()

    # OT completadas hoy
    completed_today = user_work_orders.filter(
        actual_completion__date=today
    ).count()

    # Diagnósticos pendientes
    pending_diagnostics = Diagnostics.objects.filter(
        assigned_to__user=request.user,
        status__in=['Reportada', 'Diagnostico_In_Situ']
    ).count()

    # Horas trabajadas esta semana
    week_start = now - timezone.timedelta(days=now.weekday())
    hours_this_week = user_work_orders.filter(
        mechanic_assignments__assigned_datetime__gte=week_start
    ).aggregate(
        total_hours=Sum('mechanic_assignments__hours_worked')
    )['total_hours'] or 0

    context = {
        'role': 'Mecánico',
        'features': {
            'active_work_orders': active_work_orders,
            'completed_today': completed_today,
            'pending_diagnostics': pending_diagnostics,
            'hours_this_week': round(hours_this_week, 1),
        }
    }

    return render(request, 'login/dashboard_mecanico.html', context)

@login_required
def recepcionista_vehiculos_dashboard(request):
    """Dashboard para Recepcionista de Vehículos - Ingresos, Incidentes, Diagnósticos, OT"""
    from django.utils import timezone
    from documents.models import Ingreso, Incident, WorkOrder, Diagnostics

    now = timezone.now()
    today = now.date()

    # Ingresos de hoy
    ingresos_today = Ingreso.objects.filter(
        entry_datetime__date=today
    ).count()

    # Vehículos esperando diagnóstico
    pending_diagnostics = Diagnostics.objects.filter(
        status__in=['Reportada', 'Diagnostico_In_Situ']
    ).count()

    # Órdenes de trabajo creadas hoy
    work_orders_today = WorkOrder.objects.filter(
        created_datetime__date=today
    ).count()

    # Incidentes escalados a mecánica (con diagnóstico asignado)
    escalated_incidents = Incident.objects.filter(
        diagnostics__assigned_to__isnull=False
    ).exclude(
        diagnostics__status='Resuelta'
    ).count()

    context = {
        'role': 'Recepcionista de Vehículos',
        'features': {
            'ingresos_today': ingresos_today,
            'pending_diagnostics': pending_diagnostics,
            'work_orders_today': work_orders_today,
            'escalated_incidents': escalated_incidents,
        }
    }

    return render(request, 'login/dashboard_recepcionista.html', context)

@login_required
def jefe_taller_dashboard_detailed(request):
    """Dashboard para Jefe de Taller - Diagnósticos y Órdenes de Trabajo"""
    from django.utils import timezone
    from documents.models import WorkOrder, Diagnostics

    now = timezone.now()
    today = now.date()
    this_month = now.replace(day=1)

    # Órdenes de trabajo activas
    active_work_orders = WorkOrder.objects.filter(
        status__name__in=['En Progreso', 'Pendiente']
    ).count()

    # OT completadas este mes
    completed_this_month = WorkOrder.objects.filter(
        actual_completion__gte=this_month,
        status__name='Completada'
    ).count()

    # Diagnósticos pendientes
    pending_diagnostics = Diagnostics.objects.filter(
        status__in=['Reportada', 'Diagnostico_In_Situ']
    ).count()

    # Eficiencia del taller (OT completadas vs total)
    total_work_orders_month = WorkOrder.objects.filter(
        created_datetime__gte=this_month
    ).count()

    efficiency = 0
    if total_work_orders_month > 0:
        efficiency = (completed_this_month / total_work_orders_month) * 100

    context = {
        'role': 'Jefe de taller',
        'features': {
            'active_work_orders': active_work_orders,
            'completed_this_month': completed_this_month,
            'pending_diagnostics': pending_diagnostics,
            'efficiency': round(efficiency, 1),
        }
    }

    return render(request, 'login/dashboard_jefe_taller.html', context)
