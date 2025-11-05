from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver


class Site(models.Model):
    id_site = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    patent_count = models.IntegerField()

    def __str__(self):
        return f"{self.id_site} - {self.name}"

    class Meta:
        db_table = 'Sites'


class SAPEquipment(models.Model):
    id_equipment = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.id_equipment} - {self.code}"

    class Meta:
        db_table = 'SAPEquipment'


class CECO(models.Model):
    id_ceco = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.id_ceco} - {self.name}"

    class Meta:
        db_table = 'CECO'


class VehicleType(models.Model):
    id_type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, db_column='site_id')
    data = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id_type} - {self.name}"

    class Meta:
        db_table = 'VehicleTypes'


class VehicleStatus(models.Model):
    id_status = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.id_status} - {self.name}"

    class Meta:
        db_table = 'VehicleStatus'


class Vehicle(models.Model):
    patent = models.CharField(max_length=10, primary_key=True)
    equipment = models.ForeignKey(
        SAPEquipment, on_delete=models.CASCADE, db_column='equipment_id')
    ceco = models.ForeignKey(
        CECO, on_delete=models.CASCADE, db_column='ceco_id')
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    age = models.IntegerField()
    useful_life = models.IntegerField()
    mileage = models.IntegerField(null=True, blank=True)
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, db_column='site_id')
    operational = models.BooleanField()
    backup = models.BooleanField()
    out_of_service = models.BooleanField()
    type = models.ForeignKey(
        VehicleType, on_delete=models.CASCADE, db_column='type_id')
    plan = models.BooleanField()
    sinister = models.BooleanField()
    observations = models.TextField()
    compliance = models.CharField(max_length=50)
    tct = models.CharField(max_length=50, null=True, blank=True)
    geotab_confirm = models.BooleanField()
    auction = models.BooleanField()
    status = models.ForeignKey(
        VehicleStatus, on_delete=models.SET_NULL, db_column='status_id', null=True, blank=True)

    def __str__(self):
        return self.patent

    def update_status_based_on_incidents(self):
        """
        Actualiza el estado del vehículo basado en incidencias activas.
        Si hay incidencias no resueltas, cambia a 'Fuera de servicio'.
        Si no hay, vuelve a 'Disponible' (asumiendo que no hay otros factores).
        """
        active_incidents = self.incidents.filter(diagnostics__status__in=['Reportada', 'En_revision'])
        if active_incidents.exists():
            # Asumir que hay un VehicleStatus con name='Fuera de servicio'
            out_of_service_status = VehicleStatus.objects.filter(name='Fuera de servicio').first()
            if out_of_service_status:
                self.status = out_of_service_status
        else:
            # Asumir que hay un VehicleStatus con name='Disponible'
            available_status = VehicleStatus.objects.filter(name='Disponible').first()
            if available_status:
                self.status = available_status
        self.save()

    @property
    def active_route(self):
        """
        Devuelve la ruta activa del vehículo.
        Una ruta es considerada activa si este vehículo tiene un conductor activo asignado.
        """
        # Buscar si este vehículo tiene un conductor activo
        try:
            active_driver = FlotaUser.objects.get(patent=self, status__name='Activo')
            # Si tiene conductor activo, devolver la primera ruta asociada
            return self.routes.first()
        except FlotaUser.DoesNotExist:
            return None

    class Meta:
        db_table = 'Vehicles'


class Role(models.Model):
    id_role = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_supervisor_role = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id_role} - {self.name}"

    class Meta:
        db_table = 'Role'


class UserStatus(models.Model):
    id_status = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.id_status} - {self.name}"

    class Meta:
        db_table = 'UserStatus'


class FlotaUser(models.Model):
    id_user = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='flotauser')
    name = models.CharField(max_length=100)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, db_column='role_id')
    patent = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, db_column='patent')
    status = models.ForeignKey(
        UserStatus, on_delete=models.CASCADE, db_column='status_id')
    observations = models.TextField()
    gpid = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.id_user} - {self.name}"

    class Meta:
        db_table = 'FlotaUsers'


class Route(models.Model):
    id_route = models.AutoField(primary_key=True)
    route_code = models.CharField(max_length=50)
    gtm = models.CharField(max_length=50)
    vehicles = models.ManyToManyField(
        Vehicle, db_column='route_vehicles', related_name='routes', blank=True,
        help_text='Vehículos asociados a esta ruta')
    comment = models.TextField()

    @property
    def driver(self):
        """
        Devuelve el conductor activo de esta ruta.
        Busca entre los vehículos asociados cuál tiene un conductor activo.
        """
        for vehicle in self.vehicles.all():
            try:
                flota_user = FlotaUser.objects.get(patent=vehicle, status__name='Activo')
                return flota_user
            except FlotaUser.DoesNotExist:
                continue
        return None

    def __str__(self):
        return f"{self.id_route} - {self.route_code}"

    class Meta:
        db_table = 'Routes'


class ServiceType(models.Model):
    id_service_type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, db_column='site_id')

    def __str__(self):
        return f"{self.id_service_type} - {self.name}"

    class Meta:
        db_table = 'ServiceTypes'


class MaintenanceSchedule(models.Model):
    id_schedule = models.AutoField(primary_key=True)
    patent = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, db_column='patent')
    start_datetime = models.DateTimeField()
    assigned_user = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='assigned_user_id', null=True, blank=True)
    expected_chofer = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, db_column='expected_chofer_id',
                                       null=True, blank=True, related_name='expected_ingresos')
    status = models.ForeignKey(
        UserStatus, on_delete=models.CASCADE, db_column='status_id')
    observations = models.TextField(null=True, blank=True)

    # Asociación con incidentes - permite 1 o más incidentes por agenda
    related_incidents = models.ManyToManyField(
        'Incident', blank=True, related_name='maintenance_schedules',
        help_text='Incidentes asociados a esta agenda de mantenimiento')

    def __str__(self):
        return f"{self.id_schedule} - {self.patent}"

    class Meta:
        db_table = 'MaintenanceSchedules'


class Ingreso(models.Model):
    id_ingreso = models.AutoField(primary_key=True)
    patent = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, db_column='patent')
    entry_datetime = models.DateTimeField()
    exit_datetime = models.DateTimeField(null=True, blank=True)
    chofer = models.ForeignKey(
        FlotaUser, on_delete=models.CASCADE, db_column='chofer_id')
    observations = models.TextField(null=True, blank=True)
    authorization = models.BooleanField()
    entry_registered_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='entry_registered_by_id', null=True, blank=True, related_name='entry_registered_ingresos')
    exit_registered_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='exit_registered_by_id', null=True, blank=True, related_name='exit_registered_ingresos')
    schedule = models.ForeignKey(
        MaintenanceSchedule, on_delete=models.SET_NULL, null=True, blank=True, related_name='ingresos')
    es_ingreso_tecnico = models.BooleanField(default=False, verbose_name='Es ingreso técnico')

    def __str__(self):
        return f"{self.id_ingreso} - {self.patent}"

    class Meta:
        db_table = 'Ingresos'


class WorkOrderStatus(models.Model):
    id_status = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=7, default='#6c757d')  # Color para UI

    def __str__(self):
        return f"{self.id_status} - {self.name}"

    class Meta:
        db_table = 'WorkOrderStatuses'


class WorkOrder(models.Model):
    id_work_order = models.AutoField(primary_key=True)
    ingreso = models.ForeignKey(
        Ingreso, on_delete=models.CASCADE, db_column='ingreso_id', null=True, blank=True, related_name='work_orders')
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, db_column='service_type_id', null=True, blank=True)
    status = models.ForeignKey(
        WorkOrderStatus, on_delete=models.CASCADE, db_column='status_id')
    created_datetime = models.DateTimeField(auto_now_add=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    actual_completion = models.DateTimeField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observations = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='created_by_id', null=True, blank=True, related_name='created_work_orders')
    supervisor = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='supervisor_id', null=True, blank=True, related_name='supervised_work_orders')

    def __str__(self):
        if self.ingreso:
            return f"OT-{self.id_work_order} - {self.ingreso.patent}"
        else:
            return f"OT-{self.id_work_order} - Sin ingreso"

    class Meta:
        db_table = 'WorkOrders'


class Task(models.Model):
    id_task = models.AutoField(primary_key=True)
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, db_column='work_order_id', null=True, blank=True)
    description = models.TextField()
    urgency = models.CharField(max_length=20)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, db_column='service_type_id', null=True, blank=True)
    supervisor = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='supervisor_id', null=True, blank=True)

    def __str__(self):
        return f"{self.id_task} - {self.description[:50]}"

    class Meta:
        db_table = 'Tasks'


class TaskAssignment(models.Model):
    id_assignment = models.AutoField(primary_key=True)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, db_column='task_id')
    user = models.ForeignKey(
        FlotaUser, on_delete=models.CASCADE, db_column='user_id')

    def __str__(self):
        return f"{self.id_assignment} - {self.task} - {self.user}"

    class Meta:
        db_table = 'TaskAssignments'


class Pause(models.Model):
    id_pause = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(
        TaskAssignment, on_delete=models.CASCADE, db_column='assignment_id')
    motivo = models.CharField(max_length=100)
    duration = models.IntegerField()
    authorization = models.BooleanField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.id_pause} - {self.motivo}"

    class Meta:
        db_table = 'Pauses'


class Document(models.Model):
    id_document = models.AutoField(primary_key=True)
    ingreso = models.ForeignKey(
        Ingreso, on_delete=models.CASCADE, db_column='ingreso_id')
    type = models.CharField(max_length=50)
    file_path = models.CharField(max_length=255)
    upload_datetime = models.DateTimeField()
    user = models.ForeignKey(
        FlotaUser, on_delete=models.CASCADE, db_column='user_id')

    def __str__(self):
        return f"{self.id_document} - {self.type}"

    class Meta:
        db_table = 'Documents'

# Repuesto puede ser modificado para detalles técnicos de las piezas en el futuro. Ahora Repuesto y SparePartUsage son como lo mismo, con SparePartUsage manejando el uso en OTs.
class Repuesto(models.Model):
    id_repuesto = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    task = models.ForeignKey(
        Task, on_delete=models.SET_NULL, db_column='task_id', null=True, blank=True)
    delivery_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.id_repuesto} - {self.name}"

    class Meta:
        db_table = 'Repuestos'


class Notification(models.Model):
    id_notification = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(
        FlotaUser, on_delete=models.CASCADE, db_column='recipient_id')
    message = models.TextField()
    sent_datetime = models.DateTimeField()
    type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id_notification} - {self.type}"

    class Meta:
        db_table = 'Notifications'


class Report(models.Model):
    id_report = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)
    generated_datetime = models.DateTimeField()
    data = models.JSONField()
    user = models.ForeignKey(
        FlotaUser, on_delete=models.CASCADE, db_column='user_id')

    def __str__(self):
        return f"{self.id_report} - {self.type}"

    class Meta:
        db_table = 'Reports'


class WorkOrderMechanic(models.Model):
    id_assignment = models.AutoField(primary_key=True)
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, db_column='work_order_id', related_name='mechanic_assignments')
    mechanic = models.ForeignKey(
        FlotaUser, on_delete=models.CASCADE, db_column='mechanic_id', related_name='work_order_assignments')
    assigned_datetime = models.DateTimeField(auto_now_add=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.work_order} - {self.mechanic.name}"

    class Meta:
        db_table = 'WorkOrderMechanics'


class SparePartUsage(models.Model):
    id_usage = models.AutoField(primary_key=True)
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, db_column='work_order_id', related_name='spare_part_usages')
    repuesto = models.ForeignKey(
        Repuesto, on_delete=models.CASCADE, db_column='repuesto_id')
    quantity_used = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    used_datetime = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.work_order} - {self.repuesto.name} ({self.quantity_used})"

    class Meta:
        db_table = 'SparePartUsages'


class Incident(models.Model):
    INCIDENT_TYPES = [
        ('Mecanica', 'Mecánica'),
        ('Electrica', 'Eléctrica'),
        ('Carroceria', 'Carrocería'),
        ('Neumaticos', 'Neumáticos'),
        ('Otro', 'Otro'),
    ]

    SEVERITY_LEVELS = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
        ('Critica', 'Crítica'),
    ]

    CATEGORIES = [
        ('Seguridad', 'Seguridad'),
        ('Operativo', 'Operativo'),
        ('Mantenimiento', 'Mantenimiento'),
    ]

    STATUS_CHOICES = [
        ('Reportada', 'Reportada'),
        ('Diagnostico_In_Situ', 'Diagnóstico In Situ'),
        ('OT_Generada', 'OT Generada'),
        ('Resuelta', 'Resuelta'),
    ]

    PRIORITY_LEVELS = [
        ('Baja', 'Baja'),
        ('Normal', 'Normal'),
        ('Alta', 'Alta'),
        ('Urgente', 'Urgente'),
    ]

    RESOLUTION_TYPES = [
        ('Taller', 'Taller'),
        ('Campo', 'Campo'),
        ('No_aplica', 'No aplica'),
    ]

    RESOLUTION_SOURCES = [
        ('OT_Completada', 'OT Completada'),
        ('Ingreso_Cerrado', 'Ingreso Cerrado'),
        ('Manual', 'Manual'),
    ]

    id_incident = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, db_column='vehicle_id', related_name='incidents')
    reported_by = models.ForeignKey(
        FlotaUser, on_delete=models.CASCADE, db_column='reported_by_id', related_name='reported_incidents')
    name = models.CharField(max_length=200)
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    description = models.TextField()
    location = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    is_emergency = models.BooleanField(default=False)
    requires_tow = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='created_by_id', null=True, blank=True, related_name='created_incidents')
    updated_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='updated_by_id', null=True, blank=True, related_name='updated_incidents')

    # ===== CAMPOS MOVIDOS A DIAGNOSTICS (COMENTADOS PARA REFERENCIA) =====
    # severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, null=True, blank=True)
    # category = models.CharField(max_length=50, choices=CATEGORIES, null=True, blank=True)
    # symptoms = models.TextField(null=True, blank=True)
    # possible_cause = models.TextField(null=True, blank=True)
    # route = models.ForeignKey(
    #     Route, on_delete=models.SET_NULL, db_column='route_id', null=True, blank=True, related_name='incidents')
    # status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Reportada')
    # assigned_to = models.ForeignKey(
    #     FlotaUser, on_delete=models.SET_NULL, db_column='assigned_to_id', null=True, blank=True, related_name='assigned_incidents')
    # resolved_at = models.DateTimeField(null=True, blank=True)
    # resolution_notes = models.TextField(null=True, blank=True)
    # estimated_resolution_time = models.CharField(max_length=50, null=True, blank=True)
    # affects_operation = models.BooleanField(default=False)
    # follow_up_required = models.BooleanField(default=False)
    # related_schedule = models.ForeignKey(
    #     MaintenanceSchedule, on_delete=models.SET_NULL, db_column='related_schedule_id', null=True, blank=True, related_name='incidents')
    related_ingreso = models.ForeignKey(
        Ingreso, on_delete=models.SET_NULL, db_column='related_ingreso_id', null=True, blank=True, related_name='incidents')
    # related_work_order = models.ForeignKey(
    #     WorkOrder, on_delete=models.SET_NULL, db_column='related_work_order_id', null=True, blank=True, related_name='incidents')
    # resolution_type = models.CharField(max_length=50, choices=RESOLUTION_TYPES, null=True, blank=True)
    # auto_resolved = models.BooleanField(default=False)
    # resolution_source = models.CharField(max_length=50, choices=RESOLUTION_SOURCES, null=True, blank=True)

    def __str__(self):
        return f"Incidencia #{self.id_incident} - {self.vehicle.patent} - {self.name}"

    class Meta:
        db_table = 'Incidents'


class Diagnostics(models.Model):
    """
    Modelo para diagnóstico y resolución de incidentes.
    Relación 1-1 con Incident (opcional).
    """
    DIAGNOSTIC_METHODS = [
        ('Visual', 'Visual'),
        ('Instrumentos', 'Con Instrumentos'),
        ('Prueba', 'Prueba de Funcionamiento'),
        ('Otro', 'Otro'),
    ]

    incidents = models.ManyToManyField(
        Incident, db_column='incident_ids', related_name='diagnostics', blank=True,
        help_text='Incidentes asociados a este diagnóstico')
    
    # Campo legacy para compatibilidad (se mantendrá hasta migración completa)
    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, db_column='incident_id', null=True, blank=True, related_name='legacy_diagnostics')
    
    # Campos de evaluación técnica
    severity = models.CharField(max_length=20, choices=Incident.SEVERITY_LEVELS, null=True, blank=True)
    category = models.CharField(max_length=50, choices=Incident.CATEGORIES, null=True, blank=True)
    symptoms = models.TextField(null=True, blank=True)
    possible_cause = models.TextField(null=True, blank=True)
    route = models.ForeignKey(
        Route, on_delete=models.SET_NULL, db_column='route_id', null=True, blank=True, related_name='diagnostics')
    
    # Campos de estado y asignación
    status = models.CharField(max_length=30, choices=Incident.STATUS_CHOICES, default='Reportada')
    assigned_to = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='assigned_to_id', null=True, blank=True, related_name='assigned_diagnostics')
    
    # Campos de resolución
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    estimated_resolution_time = models.CharField(max_length=50, null=True, blank=True)
    resolution_type = models.CharField(max_length=50, choices=Incident.RESOLUTION_TYPES, null=True, blank=True)
    auto_resolved = models.BooleanField(default=False)
    resolution_source = models.CharField(max_length=50, choices=Incident.RESOLUTION_SOURCES, null=True, blank=True)
    
    # Campos booleanos de impacto
    affects_operation = models.BooleanField(default=False)
    follow_up_required = models.BooleanField(default=False)
    
    # Asociaciones con otros modelos
    related_schedule = models.ForeignKey(
        MaintenanceSchedule, on_delete=models.SET_NULL, db_column='related_schedule_id', null=True, blank=True, related_name='diagnostics')
    related_ingreso = models.ForeignKey(
        Ingreso, on_delete=models.SET_NULL, db_column='related_ingreso_id', null=True, blank=True, related_name='diagnostics')
    related_work_order = models.ForeignKey(
        WorkOrder, on_delete=models.SET_NULL, db_column='related_work_order_id', null=True, blank=True, related_name='diagnostics')
    
    # Campos específicos de diagnóstico
    diagnostic_started_at = models.DateTimeField(null=True, blank=True)
    diagnostic_completed_at = models.DateTimeField(null=True, blank=True)
    diagnostic_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='diagnostic_by_id', null=True, blank=True, related_name='diagnosed_incidents')
    diagnostic_method = models.CharField(max_length=50, choices=DIAGNOSTIC_METHODS, null=True, blank=True)
    parts_needed = models.TextField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    photos_taken = models.BooleanField(default=False)
    requires_specialist = models.BooleanField(default=False)
    environmental_conditions = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True, help_text='Ubicación donde se realizó el diagnóstico (para diagnósticos in situ)')
    
    # Campos de auditoría específicos de diagnostics
    diagnostics_created_at = models.DateTimeField(auto_now_add=True)
    diagnostics_updated_at = models.DateTimeField(auto_now=True)
    diagnostics_created_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='diagnostics_created_by_id', null=True, blank=True, related_name='created_diagnostics')
    diagnostics_updated_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='diagnostics_updated_by_id', null=True, blank=True, related_name='updated_diagnostics')

    def __str__(self):
        if self.incidents.exists():
            incident_ids = list(self.incidents.values_list('id_incident', flat=True))
            return f"Diagnóstico #{self.id} - Incidentes: {', '.join(map(str, incident_ids))}"
        elif self.incident:
            return f"Diagnóstico de Incidencia #{self.incident.id_incident} (legacy)"
        return f"Diagnóstico #{self.id}"

    class Meta:
        db_table = 'Diagnostics'


class IncidentImage(models.Model):
    id_image = models.AutoField(primary_key=True)
    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, db_column='incident_id', related_name='images')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='incident_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.incident.name} - {self.name}"

    class Meta:
        db_table = 'IncidentImages'


class IngresoImage(models.Model):
    id_image = models.AutoField(primary_key=True)
    ingreso = models.ForeignKey(
        Ingreso, on_delete=models.CASCADE, db_column='ingreso_id', related_name='images')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True, help_text='Descripción del tipo de foto (ej. "Estado frontal", "Daño en neumático")')
    image = models.ImageField(upload_to='ingreso_images/')
    uploaded_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='uploaded_by_id', null=True, blank=True, related_name='uploaded_ingreso_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ingreso} - {self.name}"

    class Meta:
        db_table = 'IngresoImages'


class WorkOrderImage(models.Model):
    id_image = models.AutoField(primary_key=True)
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, db_column='work_order_id', related_name='images')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True, help_text='Descripción del tipo de foto (ej. "Trabajo realizado", "Estado final")')
    image = models.ImageField(upload_to='work_order_images/')
    uploaded_by = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='uploaded_by_id', null=True, blank=True, related_name='uploaded_work_order_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OT-{self.work_order.id_work_order} - {self.name}"

    class Meta:
        db_table = 'WorkOrderImages'


@receiver(post_save, sender=Incident)
def update_vehicle_status_on_incident_save(sender, instance, **kwargs):
    """
    Signal para actualizar el estado del vehículo cuando se guarda una incidencia.
    """
    instance.vehicle.update_status_based_on_incidents()
