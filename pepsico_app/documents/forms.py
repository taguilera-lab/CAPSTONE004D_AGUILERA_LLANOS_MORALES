from django import forms
from .models import (
    Site, SAPEquipment, CECO, VehicleType, VehicleStatus, Vehicle,
    Role, UserStatus, FlotaUser, Route, ServiceType, Ingreso,
    Task, TaskAssignment, Pause, Document, Repuesto, Notification,
    Report, MaintenanceSchedule
)

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'patent_count']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del sitio'}),
            'patent_count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad de patentes'}),
        }

class SAPEquipmentForm(forms.ModelForm):
    class Meta:
        model = SAPEquipment
        fields = ['code', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código del equipo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }

class CECOForm(forms.ModelForm):
    class Meta:
        model = CECO
        fields = ['code', 'name', 'type', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código CECO'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }

class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = ['name', 'site', 'data']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del tipo'}),
            'site': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Datos adicionales'}),
        }

class VehicleStatusForm(forms.ModelForm):
    class Meta:
        model = VehicleStatus
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del estado'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'patent', 'equipment', 'ceco', 'brand', 'model', 'year',
            'age', 'useful_life', 'mileage', 'site', 'operational',
            'backup', 'out_of_service', 'type', 'plan', 'sinister',
            'observations', 'compliance', 'tct', 'geotab_confirm',
            'auction', 'status'
        ]
        widgets = {
            'patent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patente'}),
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'ceco': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Modelo'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Año'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Edad'}),
            'useful_life': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Vida útil'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Kilometraje'}),
            'site': forms.Select(attrs={'class': 'form-control'}),
            'operational': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'backup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'out_of_service': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'plan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sinister': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones'}),
            'compliance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cumplimiento'}),
            'tct': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TCT'}),
            'geotab_confirm': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auction': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'is_supervisor_role']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del rol'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'is_supervisor_role': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserStatusForm(forms.ModelForm):
    class Meta:
        model = UserStatus
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del estado'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }

class FlotaUserForm(forms.ModelForm):
    class Meta:
        model = FlotaUser
        fields = ['name', 'role', 'patent', 'status', 'observations', 'gpid']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'patent': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones'}),
            'gpid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GPID'}),
        }

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['route_code', 'gtm', 'driver', 'truck', 'comment']
        widgets = {
            'route_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de ruta'}),
            'gtm': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GTM'}),
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'truck': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comentario'}),
        }

class ServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = ['name', 'description', 'site']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del tipo de servicio'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'site': forms.Select(attrs={'class': 'form-control'}),
        }

class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = [
            'patent', 'service_type', 'entry_datetime', 'exit_datetime',
            'chofer', 'supervisor', 'observations', 'authorization'
        ]
        widgets = {
            'patent': forms.Select(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'entry_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'exit_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'chofer': forms.Select(attrs={'class': 'form-control'}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones'}),
            'authorization': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'ingreso', 'description', 'urgency', 'start_datetime',
            'end_datetime', 'service_type', 'supervisor'
        ]
        widgets = {
            'ingreso': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'urgency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Urgencia'}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
        }

class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = TaskAssignment
        fields = ['task', 'user']
        widgets = {
            'task': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }

class PauseForm(forms.ModelForm):
    class Meta:
        model = Pause
        fields = [
            'assignment', 'motivo', 'duration', 'authorization',
            'start_datetime', 'end_datetime'
        ]
        widgets = {
            'assignment': forms.Select(attrs={'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duración'}),
            'authorization': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['ingreso', 'type', 'file_path', 'upload_datetime', 'user']
        widgets = {
            'ingreso': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo'}),
            'file_path': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ruta del archivo'}),
            'upload_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }

class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = ['name', 'quantity', 'task', 'delivery_datetime']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'task': forms.Select(attrs={'class': 'form-control'}),
            'delivery_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['recipient', 'message', 'sent_datetime', 'type']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mensaje'}),
            'sent_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo'}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['type', 'generated_datetime', 'data', 'user']
        widgets = {
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo'}),
            'generated_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Datos (JSON)'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }

class MaintenanceScheduleForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSchedule
        fields = [
            'patent', 'service_type', 'start_datetime', 'end_datetime',
            'recurrence_rule', 'reminder_minutes', 'assigned_user',
            'supervisor', 'status', 'observations'
        ]
        widgets = {
            'patent': forms.Select(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'recurrence_rule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Regla de recurrencia'}),
            'reminder_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutos de recordatorio'}),
            'assigned_user': forms.Select(attrs={'class': 'form-control'}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones'}),
        }