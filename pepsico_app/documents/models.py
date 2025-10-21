from django.db import models


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
    driver = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='driver_id', null=True, blank=True)
    truck = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, db_column='truck_patent')
    comment = models.TextField()

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
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, db_column='service_type_id', null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    recurrence_rule = models.CharField(max_length=255, null=True, blank=True)
    reminder_minutes = models.IntegerField(null=True, blank=True)
    assigned_user = models.ForeignKey(
        FlotaUser, on_delete=models.SET_NULL, db_column='assigned_user_id', null=True, blank=True)
    supervisor = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, db_column='supervisor_id',
                                   null=True, blank=True, related_name='supervised_schedules')
    expected_chofer = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, db_column='expected_chofer_id',
                                       null=True, blank=True, related_name='expected_ingresos')
    status = models.ForeignKey(
        UserStatus, on_delete=models.CASCADE, db_column='status_id')
    observations = models.TextField(null=True, blank=True)

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
    ingreso = models.OneToOneField(
        Ingreso, on_delete=models.CASCADE, db_column='ingreso_id', related_name='work_order')
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
        return f"OT-{self.id_work_order} - {self.ingreso.patent}"

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
