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

class SAPEquipmentForm(forms.ModelForm):
    class Meta:
        model = SAPEquipment
        fields = ['code', 'description']

class CECOForm(forms.ModelForm):
    class Meta:
        model = CECO
        fields = ['code', 'name', 'type', 'description']

class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = ['name', 'site', 'data']

class VehicleStatusForm(forms.ModelForm):
    class Meta:
        model = VehicleStatus
        fields = ['name', 'description']

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

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'is_supervisor_role']

class UserStatusForm(forms.ModelForm):
    class Meta:
        model = UserStatus
        fields = ['name', 'description']

class FlotaUserForm(forms.ModelForm):
    class Meta:
        model = FlotaUser
        fields = ['name', 'role', 'patent', 'status', 'observations', 'gpid']

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['route_code', 'gtm', 'driver', 'truck', 'comment']

class ServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = ['name', 'description', 'site']

class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = [
            'patent', 'service_type', 'entry_datetime', 'exit_datetime',
            'chofer', 'supervisor', 'observations', 'authorization'
        ]

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'ingreso', 'description', 'urgency', 'start_datetime',
            'end_datetime', 'service_type', 'supervisor'
        ]

class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = TaskAssignment
        fields = ['task', 'user']

class PauseForm(forms.ModelForm):
    class Meta:
        model = Pause
        fields = [
            'assignment', 'motivo', 'duration', 'authorization',
            'start_datetime', 'end_datetime'
        ]

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['ingreso', 'type', 'file_path', 'upload_datetime', 'user']

class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = ['name', 'quantity', 'task', 'delivery_datetime']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['recipient', 'message', 'sent_datetime', 'type']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['type', 'generated_datetime', 'data', 'user']

class MaintenanceScheduleForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSchedule
        fields = [
            'patent', 'service_type', 'start_datetime', 'end_datetime',
            'recurrence_rule', 'reminder_minutes', 'assigned_user',
            'supervisor', 'status', 'observations'
        ]