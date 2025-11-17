from django.contrib import admin
from .models import PauseType, WorkOrderPause

@admin.register(PauseType)
class PauseTypeAdmin(admin.ModelAdmin):
    list_display = ('id_pause_type', 'name', 'description', 'requires_authorization', 'is_active', 'created_by', 'created_at')
    list_filter = ('requires_authorization', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'created_by__name')
    ordering = ('-created_at',)
    readonly_fields = ('id_pause_type', 'created_at', 'updated_at')


@admin.register(WorkOrderPause)
class WorkOrderPauseAdmin(admin.ModelAdmin):
    list_display = ('id_pause', 'work_order', 'mechanic_assignment', 'pause_type', 'reason', 'start_datetime', 'end_datetime', 'duration_display', 'is_active', 'requires_authorization', 'authorized_by')
    list_filter = ('is_active', 'requires_authorization', 'pause_type', 'start_datetime', 'end_datetime', 'authorized_at')
    search_fields = ('work_order__id_work_order', 'mechanic_assignment__mechanic__name', 'pause_type__name', 'reason', 'authorized_by__name')
    ordering = ('-start_datetime',)
    readonly_fields = ('id_pause', 'created_at', 'updated_at', 'duration_minutes')
