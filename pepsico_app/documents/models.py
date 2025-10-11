from django.db import models

class Site(models.Model):
    id_site = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    patent_count = models.IntegerField()

    class Meta:
        db_table = 'Sites'

class SAPEquipment(models.Model):
    id_equipment = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'SAPEquipment'

class CECO(models.Model):
    id_ceco = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'CECO'

class VehicleType(models.Model):
    id_type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, db_column='site_id')
    data = models.CharField(max_length=50)

    class Meta:
        db_table = 'VehicleTypes'

class VehicleStatus(models.Model):
    id_status = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'VehicleStatus'

class Vehicle(models.Model):
    patent = models.CharField(max_length=10, primary_key=True)
    equipment = models.ForeignKey(SAPEquipment, on_delete=models.CASCADE, db_column='equipment_id')
    ceco = models.ForeignKey(CECO, on_delete=models.CASCADE, db_column='ceco_id')
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    age = models.IntegerField()
    useful_life = models.IntegerField()
    mileage = models.IntegerField(null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, db_column='site_id')
    operational = models.BooleanField()
    backup = models.BooleanField()
    out_of_service = models.BooleanField()
    type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, db_column='type_id')
    plan = models.BooleanField()
    sinister = models.BooleanField()
    observations = models.TextField()
    compliance = models.CharField(max_length=50)
    tct = models.CharField(max_length=50, null=True, blank=True)
    geotab_confirm = models.BooleanField()
    auction = models.BooleanField()
    status = models.ForeignKey(VehicleStatus, on_delete=models.SET_NULL, db_column='status_id', null=True, blank=True)

    class Meta:
        db_table = 'Vehicles'

class Role(models.Model):
    id_role = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_supervisor_role = models.BooleanField(default=False)

    class Meta:
        db_table = 'Role'

class UserStatus(models.Model):
    id_status = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'UserStatus'

class FlotaUser(models.Model):
    id_user = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')
    patent = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column='patent')
    status = models.ForeignKey(UserStatus, on_delete=models.CASCADE, db_column='status_id')
    observations = models.TextField()
    gpid = models.CharField(max_length=20)

    class Meta:
        db_table = 'FlotaUsers'

class Route(models.Model):
    id_route = models.AutoField(primary_key=True)
    route_code = models.CharField(max_length=50)
    gtm = models.CharField(max_length=50)
    driver = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, db_column='driver_id', null=True, blank=True)
    truck = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column='truck_patent')
    comment = models.TextField()

    class Meta:
        db_table = 'Routes'

class ServiceType(models.Model):
    id_service_type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, db_column='site_id')

    class Meta:
        db_table = 'ServiceTypes'

class Ingreso(models.Model):
    id_ingreso = models.AutoField(primary_key=True)
    patent = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column='patent')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, db_column='service_type_id')
    entry_datetime = models.DateTimeField()
    exit_datetime = models.DateTimeField(null=True, blank=True)
    chofer = models.ForeignKey(FlotaUser, on_delete=models.CASCADE, db_column='chofer_id')
    supervisor = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, db_column='supervisor_id', null=True, blank=True, related_name='supervised_ingresos')
    observations = models.TextField(null=True, blank=True)
    authorization = models.BooleanField()

    class Meta:
        db_table = 'Ingresos'

class Task(models.Model):
    id_task = models.AutoField(primary_key=True)
    ingreso = models.ForeignKey(Ingreso, on_delete=models.CASCADE, db_column='ingreso_id')
    description = models.TextField()
    urgency = models.CharField(max_length=20)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, db_column='service_type_id')
    supervisor = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, db_column='supervisor_id', null=True, blank=True)

    class Meta:
        db_table = 'Tasks'

class TaskAssignment(models.Model):
    id_assignment = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, db_column='task_id')
    user = models.ForeignKey(FlotaUser, on_delete=models.CASCADE, db_column='user_id')

    class Meta:
        db_table = 'TaskAssignments'

class Pause(models.Model):
    id_pause = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(TaskAssignment, on_delete=models.CASCADE, db_column='assignment_id')
    motivo = models.CharField(max_length=100)
    duration = models.IntegerField()
    authorization = models.BooleanField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    class Meta:
        db_table = 'Pauses'

class Document(models.Model):
    id_document = models.AutoField(primary_key=True)
    ingreso = models.ForeignKey(Ingreso, on_delete=models.CASCADE, db_column='ingreso_id')
    type = models.CharField(max_length=50)
    file_path = models.CharField(max_length=255)
    upload_datetime = models.DateTimeField()
    user = models.ForeignKey(FlotaUser, on_delete=models.CASCADE, db_column='user_id')

    class Meta:
        db_table = 'Documents'

class Repuesto(models.Model):
    id_repuesto = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, db_column='task_id', null=True, blank=True)
    delivery_datetime = models.DateTimeField()

    class Meta:
        db_table = 'Repuestos'

class Notification(models.Model):
    id_notification = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(FlotaUser, on_delete=models.CASCADE, db_column='recipient_id')
    message = models.TextField()
    sent_datetime = models.DateTimeField()
    type = models.CharField(max_length=50)

    class Meta:
        db_table = 'Notifications'

class Report(models.Model):
    id_report = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)
    generated_datetime = models.DateTimeField()
    data = models.JSONField()
    user = models.ForeignKey(FlotaUser, on_delete=models.CASCADE, db_column='user_id')

    class Meta:
        db_table = 'Reports'

class MaintenanceSchedule(models.Model):
    id_schedule = models.AutoField(primary_key=True)
    patent = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column='patent')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, db_column='service_type_id')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    recurrence_rule = models.CharField(max_length=255, null=True, blank=True)
    reminder_minutes = models.IntegerField(null=True, blank=True)
    assigned_user = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, db_column='assigned_user_id', null=True, blank=True)
    supervisor = models.ForeignKey(FlotaUser, on_delete=models.SET_NULL, db_column='supervisor_id', null=True, blank=True, related_name='supervised_schedules')
    status = models.ForeignKey(UserStatus, on_delete=models.CASCADE, db_column='status_id')
    observations = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'MaintenanceSchedules'