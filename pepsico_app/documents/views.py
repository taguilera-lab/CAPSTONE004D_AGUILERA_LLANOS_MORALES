from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.apps import apps
from .models import Site, SAPEquipment, CECO, VehicleType, VehicleStatus, Vehicle, Role, UserStatus, FlotaUser, Route, Ingreso, ServiceType, Task, TaskAssignment, Pause, Document, Repuesto, Notification, Report, MaintenanceSchedule
from .forms import (
    SiteForm, SAPEquipmentForm, CECOForm, VehicleTypeForm, VehicleStatusForm, VehicleForm,
    RoleForm, UserStatusForm, FlotaUserForm, RouteForm, ServiceTypeForm, IngresoForm,
    TaskForm, TaskAssignmentForm, PauseForm, DocumentForm, RepuestoForm, NotificationForm,
    ReportForm, MaintenanceScheduleForm
)

def edit_form(request, modelo, pk):
    modelos = {
        'sites': Site,
        'sap_equipments': SAPEquipment,
        'cecos': CECO,
        'vehicle_types': VehicleType,
        'vehicle_statuses': VehicleStatus,
        'vehicles': Vehicle,
        'roles': Role,
        'user_statuses': UserStatus,
        'flota_users': FlotaUser,
        'routes': Route,
        'ingresos': Ingreso,
        'service_types': ServiceType,
        'tasks': Task,
        'task_assignments': TaskAssignment,
        'pauses': Pause,
        'documents': Document,
        'repuestos': Repuesto,
        'notifications': Notification,
        'reports': Report,
        'maintenance_schedules': MaintenanceSchedule,
    }

    table_names = {
        'sites': 'Sites',
        'sap_equipments': 'SAP Equipment',
        'cecos': 'CECO',
        'vehicle_types': 'Tipos de Vehículos',
        'vehicle_statuses': 'Estados de Vehículos',
        'vehicles': 'Vehículos',
        'roles': 'Roles',
        'user_statuses': 'Estados de Usuarios',
        'flota_users': 'Usuarios de Flota',
        'routes': 'Rutas',
        'service_types': 'Tipos de Servicio',
        'ingresos': 'Ingresos',
        'tasks': 'Tareas',
        'task_assignments': 'Asignaciones de Tareas',
        'pauses': 'Pausas',
        'documents': 'Documentos',
        'repuestos': 'Repuestos',
        'notifications': 'Notificaciones',
        'reports': 'Reportes',
        'maintenance_schedules': 'Programaciones de Mantenimiento',
    }

    if modelo not in modelos:
        messages.error(request, 'Modelo no válido')
        return redirect('datos')

    model_class = modelos[modelo]
    try:
        instance = model_class.objects.get(pk=pk)
    except model_class.DoesNotExist:
        messages.error(request, 'Registro no encontrado')
        return redirect('datos')

    # Map modelo to form_key
    modelo_to_form_key = {
        'sites': 'site',
        'sap_equipments': 'sap_equipment',
        'cecos': 'ceco',
        'vehicle_types': 'vehicle_type',
        'vehicle_statuses': 'vehicle_status',
        'vehicles': 'vehicle',
        'roles': 'role',
        'user_statuses': 'user_status',
        'flota_users': 'flota_user',
        'routes': 'route',
        'service_types': 'service_type',
        'ingresos': 'ingreso',
        'tasks': 'task',
        'task_assignments': 'task_assignment',
        'pauses': 'pause',
        'documents': 'document',
        'repuestos': 'repuesto',
        'notifications': 'notification',
        'reports': 'report',
        'maintenance_schedules': 'maintenance_schedule',
    }
    
    form_key = modelo_to_form_key.get(modelo)
    if not form_key:
        messages.error(request, 'Modelo no válido')
        return redirect('datos')
    
    # Map form keys to form classes
    form_classes = {
        'site': SiteForm,
        'sap_equipment': SAPEquipmentForm,
        'ceco': CECOForm,
        'vehicle_type': VehicleTypeForm,
        'vehicle_status': VehicleStatusForm,
        'vehicle': VehicleForm,
        'role': RoleForm,
        'user_status': UserStatusForm,
        'flota_user': FlotaUserForm,
        'route': RouteForm,
        'service_type': ServiceTypeForm,
        'ingreso': IngresoForm,
        'task': TaskForm,
        'task_assignment': TaskAssignmentForm,
        'pause': PauseForm,
        'document': DocumentForm,
        'repuesto': RepuestoForm,
        'notification': NotificationForm,
        'report': ReportForm,
        'maintenance_schedule': MaintenanceScheduleForm,
    }
    
    if form_key not in form_classes:
        messages.error(request, 'Formulario no encontrado')
        return redirect('datos')
    
    form_class = form_classes[form_key]
    form = form_class(instance=instance)

    # Create all forms but only populate the editing one
    forms = {
        'site': SiteForm(),
        'sap_equipment': SAPEquipmentForm(),
        'ceco': CECOForm(),
        'vehicle_type': VehicleTypeForm(),
        'vehicle_status': VehicleStatusForm(),
        'vehicle': VehicleForm(),
        'role': RoleForm(),
        'user_status': UserStatusForm(),
        'flota_user': FlotaUserForm(),
        'route': RouteForm(),
        'service_type': ServiceTypeForm(),
        'ingreso': IngresoForm(),
        'task': TaskForm(),
        'task_assignment': TaskAssignmentForm(),
        'pause': PauseForm(),
        'document': DocumentForm(),
        'repuesto': RepuestoForm(),
        'notification': NotificationForm(),
        'report': ReportForm(),
        'maintenance_schedule': MaintenanceScheduleForm(),
    }
    forms[form_key] = form  # Replace with the instance form

    if request.method == 'POST':
        form = form_class(request.POST)
        form.instance = instance
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Se ha editado un registro en {table_names.get(modelo, "Tabla")}.')
                return redirect('datos')
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
        else:
            forms[form_key] = form

    return render(request, 'documents/form.html', {
        'forms': forms,
        'is_edit': True,
        'table_name': table_names.get(modelo, 'Tabla'),
        'selected_form': form_key
    })

@require_POST
def eliminar_registros(request):
    modelo_nombre = request.POST.get('modelo')
    ids = request.POST.getlist('ids[]')

    # Mapa de nombres de modelos a clases
    modelos = {
        'sites': Site,
        'sap_equipments': SAPEquipment,
        'cecos': CECO,
        'vehicle_types': VehicleType,
        'vehicle_statuses': VehicleStatus,
        'vehicles': Vehicle,
        'roles': Role,
        'user_statuses': UserStatus,
        'flota_users': FlotaUser,
        'routes': Route,
        'ingresos': Ingreso,
        'service_types': ServiceType,
        'tasks': Task,
        'task_assignments': TaskAssignment,
        'pauses': Pause,
        'documents': Document,
        'repuestos': Repuesto,
        'notifications': Notification,
        'reports': Report,
        'maintenance_schedules': MaintenanceSchedule,
    }

    if modelo_nombre not in modelos:
        return JsonResponse({'success': False, 'message': 'Modelo no válido'})

    modelo = modelos[modelo_nombre]
    ids_validos = [int(id) for id in ids if id.isdigit()]

    if not ids_validos:
        return JsonResponse({'success': False, 'message': 'No se proporcionaron IDs válidos'})

    try:
        deleted, _ = modelo.objects.filter(pk__in=ids_validos).delete()
        return JsonResponse({'success': True, 'message': f'{deleted} registro(s) eliminado(s)'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al eliminar: {str(e)}'})

def datos(request):
    context = {
        'sites': Site.objects.all(),
        'sap_equipments': SAPEquipment.objects.all(),
        'cecos': CECO.objects.all(),
        'vehicle_types': VehicleType.objects.all(),
        'vehicle_statuses': VehicleStatus.objects.all(),
        'vehicles': Vehicle.objects.all(),
        'roles': Role.objects.all(),
        'user_statuses': UserStatus.objects.all(),
        'flota_users': FlotaUser.objects.all(),
        'routes': Route.objects.all(),
        'ingresos': Ingreso.objects.all(),
        'service_types': ServiceType.objects.all(),
        'tasks': Task.objects.all(),
        'task_assignments': TaskAssignment.objects.all(),
        'pauses': Pause.objects.all(),
        'documents': Document.objects.all(),
        'repuestos': Repuesto.objects.all(),
        'notifications': Notification.objects.all(),
        'reports': Report.objects.all(),
        'maintenance_schedules': MaintenanceSchedule.objects.all(),
    }
    return render(request, 'documents/datos.html', context)

def busqueda_patente(request):
    context = {
        'vehicles': Vehicle.objects.all(),
        'ingresos': Ingreso.objects.all(),
        'routes': Route.objects.all(),
        'maintenance_schedules': MaintenanceSchedule.objects.all(),
        'flota_users': FlotaUser.objects.all(),
    }
    return render(request, 'documents/busqueda-patente.html', context)

def create_form(request):
    forms = {
        'site': SiteForm(),
        'sap_equipment': SAPEquipmentForm(),
        'ceco': CECOForm(),
        'vehicle_type': VehicleTypeForm(),
        'vehicle_status': VehicleStatusForm(),
        'vehicle': VehicleForm(),
        'role': RoleForm(),
        'user_status': UserStatusForm(),
        'flota_user': FlotaUserForm(),
        'route': RouteForm(),
        'service_type': ServiceTypeForm(),
        'ingreso': IngresoForm(),
        'task': TaskForm(),
        'task_assignment': TaskAssignmentForm(),
        'pause': PauseForm(),
        'document': DocumentForm(),
        'repuesto': RepuestoForm(),
        'notification': NotificationForm(),
        'report': ReportForm(),
        'maintenance_schedule': MaintenanceScheduleForm(),
    }

    table_names = {
        'site': 'Sites',
        'sap_equipment': 'SAP Equipment',
        'ceco': 'CECO',
        'vehicle_type': 'Tipos de Vehículos',
        'vehicle_status': 'Estados de Vehículos',
        'vehicle': 'Vehículos',
        'role': 'Roles',
        'user_status': 'Estados de Usuarios',
        'flota_user': 'Usuarios de Flota',
        'route': 'Rutas',
        'service_type': 'Tipos de Servicio',
        'ingreso': 'Ingresos',
        'task': 'Tareas',
        'task_assignment': 'Asignaciones de Tareas',
        'pause': 'Pausas',
        'document': 'Documentos',
        'repuesto': 'Repuestos',
        'notification': 'Notificaciones',
        'report': 'Reportes',
        'maintenance_schedule': 'Programaciones de Mantenimiento',
    }

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type in forms:
            # Map form keys to form classes
            form_classes = {
                'site': SiteForm,
                'sap_equipment': SAPEquipmentForm,
                'ceco': CECOForm,
                'vehicle_type': VehicleTypeForm,
                'vehicle_status': VehicleStatusForm,
                'vehicle': VehicleForm,
                'role': RoleForm,
                'user_status': UserStatusForm,
                'flota_user': FlotaUserForm,
                'route': RouteForm,
                'service_type': ServiceTypeForm,
                'ingreso': IngresoForm,
                'task': TaskForm,
                'task_assignment': TaskAssignmentForm,
                'pause': PauseForm,
                'document': DocumentForm,
                'repuesto': RepuestoForm,
                'notification': NotificationForm,
                'report': ReportForm,
                'maintenance_schedule': MaintenanceScheduleForm,
            }
            form_class = form_classes[form_type]
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f'Se ha creado un nuevo registro en {table_names.get(form_type, "Tabla")}.')
                return redirect('datos')
            else:
                forms[form_type] = form  # Update with errors

    return render(request, 'documents/form.html', {'forms': forms})