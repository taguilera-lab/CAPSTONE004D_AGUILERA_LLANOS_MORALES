from django.db import models
from django.utils import timezone
from datetime import datetime, time, timedelta
from documents.models import WorkOrder, WorkOrderMechanic, FlotaUser

class PauseType(models.Model):
    """Tipos de pausa disponibles"""
    id_pause_type = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    requires_authorization = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, null=True, related_name='created_pause_types')
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, null=True, related_name='updated_pause_types')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'PauseTypes'
        verbose_name = 'Tipo de Pausa'
        verbose_name_plural = 'Tipos de Pausa'


class WorkOrderPause(models.Model):
    """Pausas en órdenes de trabajo"""
    id_pause = models.AutoField(primary_key=True)
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, related_name='pauses'
    )
    mechanic_assignment = models.ForeignKey(
        WorkOrderMechanic, on_delete=models.CASCADE, null=True, blank=True,
        related_name='pauses'
    )
    pause_type = models.ForeignKey(
        PauseType, on_delete=models.CASCADE
    )

    # Información de la pausa
    reason = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)  # Duración en minutos

    # Estado y autorización
    is_active = models.BooleanField(default=True)
    requires_authorization = models.BooleanField(default=False)
    is_personal_pause = models.BooleanField(default=False)  # Pausas registradas por mecánicos
    authorized_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='authorized_pauses'
    )
    authorized_at = models.DateTimeField(null=True, blank=True)

    # Usuario que registra la pausa
    created_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_pauses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Información adicional para pausas por stock
    affected_spare_part = models.ForeignKey(
        'documents.Repuesto', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_pauses'
    )
    required_quantity = models.IntegerField(null=True, blank=True)
    available_quantity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        mechanic_name = self.mechanic_assignment.mechanic.name if self.mechanic_assignment else "General"
        return f"OT-{self.work_order.id_work_order} - {self.pause_type.name} - {mechanic_name}"

    def save(self, *args, **kwargs):
        # Calcular duración si end_datetime está establecido
        if self.end_datetime and self.start_datetime:
            self.duration_minutes = self.calculate_working_hours_duration()

        # Establecer si requiere autorización basado en el tipo de pausa
        if self.pause_type:
            self.requires_authorization = self.pause_type.requires_authorization

        super().save(*args, **kwargs)

    def calculate_working_hours_duration(self):
        """Calcula la duración de la pausa TOTAL (sin restricción de horario laboral)"""
        if not self.end_datetime or not self.start_datetime:
            return 0

        # TEMPORALMENTE COMENTADO: Cálculo considerando solo horario laboral (7:30 AM - 4:30 PM)
        """
        start = self.start_datetime
        end = self.end_datetime

        # Horario laboral: 7:30 AM - 4:30 PM
        work_start = time(7, 30)
        work_end = time(16, 30)

        total_duration = 0

        # Si la pausa está dentro del mismo día
        if start.date() == end.date():
            # Ajustar start y end al horario laboral
            effective_start = max(start.time(), work_start) if start.time() >= work_start else work_start
            effective_end = min(end.time(), work_end) if end.time() <= work_end else work_end

            if effective_start < effective_end:
                duration = datetime.combine(start.date(), effective_end) - datetime.combine(start.date(), effective_start)
                total_duration = duration.total_seconds() / 60
        else:
            # Pausa que cruza días
            current_date = start.date()

            # Día de inicio
            if start.time() < work_end:
                effective_start = max(start.time(), work_start)
                effective_end = work_end
                if effective_start < effective_end:
                    duration = datetime.combine(current_date, effective_end) - datetime.combine(current_date, effective_start)
                    total_duration += duration.total_seconds() / 60

            # Días completos entre inicio y fin
            current_date += timedelta(days=1)
            while current_date < end.date():
                # Día completo de trabajo
                duration = datetime.combine(current_date, work_end) - datetime.combine(current_date, work_start)
                total_duration += duration.total_seconds() / 60
                current_date += timedelta(days=1)

            # Día de fin
            if end.time() > work_start:
                effective_start = work_start
                effective_end = min(end.time(), work_end)
                if effective_start < effective_end:
                    duration = datetime.combine(end.date(), effective_end) - datetime.combine(end.date(), effective_start)
                    total_duration += duration.total_seconds() / 60

        return int(total_duration)
        """

        # CÁLCULO TEMPORAL: Duración total sin restricciones de horario laboral
        duration = self.end_datetime - self.start_datetime
        return int(duration.total_seconds() / 60)

    def calculate_working_hours_duration_active(self):
        """Calcula la duración efectiva de una pausa activa dentro del horario laboral"""
        if self.end_datetime:
            return self.duration_minutes or 0
        
        # Para pausa activa, calcular hasta ahora
        from django.utils import timezone
        now = timezone.now()
        
        # Crear una pausa temporal con end_datetime = now
        temp_pause = WorkOrderPause(
            start_datetime=self.start_datetime,
            end_datetime=now
        )
        
        return temp_pause.calculate_working_hours_duration()

    @property
    def is_completed(self):
        """Verifica si la pausa ha terminado"""
        return self.end_datetime is not None

    @property
    def duration_display(self):
        """Muestra la duración en formato legible"""
        if self.end_datetime and self.start_datetime:
            # Si la pausa está terminada, calcular duración en tiempo real
            duration_minutes = self.calculate_working_hours_duration()
            if duration_minutes > 0:
                hours = duration_minutes // 60
                minutes = duration_minutes % 60
                if hours > 0:
                    return f"{hours}h {minutes}m"
                else:
                    return f"{minutes}m"
            else:
                return "Completada (0m)"
        elif self.duration_minutes:
            # Usar duración pre-calculada si existe
            hours = self.duration_minutes // 60
            minutes = self.duration_minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        else:
            return "En curso"

    class Meta:
        db_table = 'WorkOrderPauses'
        verbose_name = 'Pausa de Orden de Trabajo'
        verbose_name_plural = 'Pausas de Órdenes de Trabajo'
        ordering = ['-start_datetime']
