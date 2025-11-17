from django.contrib import admin
from .models import (
    Site, SAPEquipment, CECO, VehicleType, VehicleStatus, Vehicle,
    Role, UserStatus, FlotaUser, Route, ServiceType, Ingreso,
    Task, TaskAssignment, Pause, Document, Repuesto, Notification,
    Report, MaintenanceSchedule, Incident, IncidentImage, IngresoImage
)

# Register your models here.

admin.site.register(Site)
admin.site.register(SAPEquipment)
admin.site.register(CECO)
admin.site.register(VehicleType)
admin.site.register(VehicleStatus)
admin.site.register(Vehicle)
admin.site.register(Role)
admin.site.register(UserStatus)
admin.site.register(FlotaUser)
admin.site.register(Route)
admin.site.register(ServiceType)
admin.site.register(Ingreso)
admin.site.register(Document)
admin.site.register(Notification)
admin.site.register(Report)
admin.site.register(MaintenanceSchedule)
admin.site.register(Incident)
admin.site.register(IncidentImage)
admin.site.register(IngresoImage)


# Clases de admin personalizadas para mejor gestión

@admin.register(Pause)
class PauseAdmin(admin.ModelAdmin):
    list_display = ('id_pause', 'assignment', 'motivo', 'duration', 'authorization', 'start_datetime', 'end_datetime')
    list_filter = ('authorization', 'start_datetime', 'end_datetime')
    search_fields = ('motivo', 'assignment__task__description', 'assignment__user__name')
    ordering = ('-start_datetime',)
    readonly_fields = ('id_pause',)


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ('id_repuesto', 'name', 'quantity', 'task', 'delivery_datetime')
    list_filter = ('delivery_datetime', 'task__work_order')
    search_fields = ('name', 'task__description', 'task__work_order__id_work_order')
    ordering = ('-delivery_datetime',)
    readonly_fields = ('id_repuesto',)
