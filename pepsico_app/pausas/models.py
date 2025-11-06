from django.db import models
from django.utils import timezone
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
            duration = self.end_datetime - self.start_datetime
            self.duration_minutes = int(duration.total_seconds() / 60)

        # Establecer si requiere autorización basado en el tipo de pausa
        if self.pause_type:
            self.requires_authorization = self.pause_type.requires_authorization

        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        """Verifica si la pausa ha terminado"""
        return self.end_datetime is not None

    @property
    def duration_display(self):
        """Muestra la duración en formato legible"""
        if self.duration_minutes:
            hours = self.duration_minutes // 60
            minutes = self.duration_minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        return "En curso"

    class Meta:
        db_table = 'WorkOrderPauses'
        verbose_name = 'Pausa de Orden de Trabajo'
        verbose_name_plural = 'Pausas de Órdenes de Trabajo'
        ordering = ['-start_datetime']
