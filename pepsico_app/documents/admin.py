from django.contrib import admin
from .models import (
    Site, SAPEquipment, CECO, VehicleType, VehicleStatus, Vehicle,
    Role, UserStatus, FlotaUser, Route, ServiceType, Ingreso,
    Task, TaskAssignment, Pause, Document, Repuesto, Notification,
    Report, MaintenanceSchedule
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
admin.site.register(Task)
admin.site.register(TaskAssignment)
admin.site.register(Pause)
admin.site.register(Document)
admin.site.register(Repuesto)
admin.site.register(Notification)
admin.site.register(Report)
admin.site.register(MaintenanceSchedule)
