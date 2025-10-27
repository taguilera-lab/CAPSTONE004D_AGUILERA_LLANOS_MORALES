import os
import django
import random
from faker import Faker
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pepsico_app.settings')
django.setup()

from documents.models import Site, SAPEquipment, CECO, VehicleType, VehicleStatus, Vehicle, Role, UserStatus, FlotaUser, Route, ServiceType, Ingreso, Task, TaskAssignment, Pause, Document, Repuesto, Notification, Report, MaintenanceSchedule, WorkOrder, WorkOrderStatus, Incident, WorkOrderMechanic, SparePartUsage, Diagnostics, IncidentImage, IngresoImage
from django.contrib.auth.models import User

fake = Faker('es_ES')

def populate_db():
    # Limpiar base de datos
    User.objects.all().delete()
    Site.objects.all().delete()
    SAPEquipment.objects.all().delete()
    CECO.objects.all().delete()
    VehicleType.objects.all().delete()
    VehicleStatus.objects.all().delete()
    Vehicle.objects.all().delete()
    Role.objects.all().delete()
    UserStatus.objects.all().delete()
    FlotaUser.objects.all().delete()
    Route.objects.all().delete()
    ServiceType.objects.all().delete()
    Ingreso.objects.all().delete()
    Task.objects.all().delete()
    TaskAssignment.objects.all().delete()
    Pause.objects.all().delete()
    Document.objects.all().delete()
    Repuesto.objects.all().delete()
    Notification.objects.all().delete()
    Report.objects.all().delete()
    MaintenanceSchedule.objects.all().delete()
    WorkOrder.objects.all().delete()
    WorkOrderStatus.objects.all().delete()
    Incident.objects.all().delete()
    WorkOrderMechanic.objects.all().delete()
    SparePartUsage.objects.all().delete()
    Diagnostics.objects.all().delete()
    IncidentImage.objects.all().delete()
    IngresoImage.objects.all().delete()

    # Poblar Sites
    sites = []
    for _ in range(5):
        site = Site.objects.create(
            name=fake.city(),
            patent_count=random.randint(10, 50)
        )
        sites.append(site)

    # Poblar SAPEquipment
    equipments = []
    for _ in range(10):
        equipment = SAPEquipment.objects.create(
            code=f"EQP{fake.unique.random_int(min=1000, max=9999)}",
            description=fake.text(max_nb_chars=200) if random.choice([True, False]) else None
        )
        equipments.append(equipment)

    # Poblar CECO
    cecos = []
    for _ in range(5):
        ceco = CECO.objects.create(
            code=f"C{fake.unique.random_int(min=100, max=999)}",
            name=f"Flota {fake.word().capitalize()}",
            type=random.choice(['Operativa', 'Mantenimiento', 'Logística']),
            description=fake.text(max_nb_chars=200) if random.choice([True, False]) else None
        )
        cecos.append(ceco)

    # Poblar VehicleTypes
    vehicle_types = []
    for _ in range(5):
        vehicle_type = VehicleType.objects.create(
            name=fake.word().capitalize(),
            site=random.choice(sites),
            data=fake.word()
        )
        vehicle_types.append(vehicle_type)

    # Poblar VehicleStatus
    vehicle_statuses = []
    for status_name in ['Operativo', 'Estacionado', 'En reparación', 'Fuera de servicio', 'Disponible']:
        status = VehicleStatus.objects.create(
            name=status_name,
            description=fake.text(max_nb_chars=200)
        )
        vehicle_statuses.append(status)

    # Poblar Vehicles
    vehicles = []
    for _ in range(20):
        vehicle = Vehicle.objects.create(
            patent=fake.unique.license_plate(),
            equipment=random.choice(equipments),
            ceco=random.choice(cecos),
            brand=fake.company(),
            model=fake.word().capitalize(),
            year=random.randint(2010, 2023),
            age=random.randint(1, 15),
            useful_life=random.randint(5, 20),
            mileage=random.randint(10000, 200000),
            site=random.choice(sites),
            operational=random.choice([True, False]),
            backup=random.choice([True, False]),
            out_of_service=random.choice([True, False]),
            type=random.choice(vehicle_types),
            plan=random.choice([True, False]),
            sinister=random.choice([True, False]),
            observations=fake.text(max_nb_chars=200),
            compliance=fake.word(),
            tct=fake.word(),
            geotab_confirm=random.choice([True, False]),
            auction=random.choice([True, False]),
            status=random.choice(vehicle_statuses)
        )
        vehicles.append(vehicle)

    # Poblar Role
    roles = []
    role_names = ['Jefe de Flota', 'Mecánico', 'Vendedor', 'Guardia', 'Bodeguero', 'Supervisor', 'Jefe de taller', 'Recepcionista de Vehículos', 'Administrador']
    for role_name in role_names:
        role = Role.objects.create(
            name=role_name,
            description=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
            is_supervisor_role=role_name in ['Jefe de Flota', 'Supervisor', 'Jefe de taller', 'Administrador']
        )
        roles.append(role)

    # Poblar UserStatus
    user_statuses = []
    for status_name in ['Activo', 'Inactivo', 'En capacitación']:
        status = UserStatus.objects.create(
            name=status_name,
            description=fake.text(max_nb_chars=200) if random.choice([True, False]) else None
        )
        user_statuses.append(status)

    # Poblar FlotaUsers - Usuarios por defecto
    flota_users = []
    
    # Usuarios específicos
    default_users = [
        {'username': 'jefe_de_flota', 'password': '123', 'role_name': 'Jefe de Flota', 'name': 'Jefe de Flota'},
        {'username': 'mecanico', 'password': '123', 'role_name': 'Mecánico', 'name': 'Mecánico'},
        {'username': 'vendedor', 'password': '123', 'role_name': 'Vendedor', 'name': 'Vendedor'},
        {'username': 'guardia', 'password': '123', 'role_name': 'Guardia', 'name': 'Guardia'},
        {'username': 'bodeguero', 'password': '123', 'role_name': 'Bodeguero', 'name': 'Bodeguero'},
        {'username': 'supervisor', 'password': '123', 'role_name': 'Supervisor', 'name': 'Supervisor'},
        {'username': 'jefe_de_taller', 'password': '123', 'role_name': 'Jefe de taller', 'name': 'Jefe de Taller'},
        {'username': 'recepcionista_de_vehículos', 'password': '123', 'role_name': 'Recepcionista de Vehículos', 'name': 'Recepcionista de Vehículos'},
    ]
    
    for user_data in default_users:
        user_django = User.objects.create_user(
            username=user_data['username'],
            email=f"{user_data['username']}@example.com",
            password=user_data['password']
        )
        role = next(r for r in roles if r.name == user_data['role_name'])
        user = FlotaUser.objects.create(
            user=user_django,
            name=user_data['name'],
            role=role,
            patent=random.choice(vehicles),
            status=random.choice(user_statuses),
            observations=fake.text(max_nb_chars=200),
            gpid=f"GP{fake.unique.random_int(min=1000, max=9999)}"
        )
        flota_users.append(user)
    
    # Poblar usuarios adicionales aleatorios
    for _ in range(7):  # Total 15 usuarios, 8 específicos + 7 aleatorios
        user_django = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password='password123'
        )
        user = FlotaUser.objects.create(
            user=user_django,
            name=fake.name(),
            role=random.choice(roles),
            patent=random.choice(vehicles),
            status=random.choice(user_statuses),
            observations=fake.text(max_nb_chars=200),
            gpid=f"GP{fake.unique.random_int(min=1000, max=9999)}"
        )
        flota_users.append(user)

    # Poblar Routes
    routes = []
    for _ in range(10):
        route = Route.objects.create(
            route_code=f"R{fake.unique.random_int(min=100, max=999)}",
            gtm=fake.word(),
            driver=random.choice(flota_users) if random.choice([True, False]) else None,
            truck=random.choice(vehicles),
            comment=fake.text(max_nb_chars=200)
        )
        routes.append(route)

    # Poblar ServiceTypes
    service_types = []
    for service_name in ['Siniestro', 'Taller Automarket', 'Potrero', 'Mantenimiento General']:
        service_type = ServiceType.objects.create(
            name=service_name,
            description=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
            site=random.choice(sites)
        )
        service_types.append(service_type)

    # Poblar Ingresos
    ingresos = []
    for _ in range(15):
        ingreso = Ingreso.objects.create(
            patent=random.choice(vehicles),
            entry_datetime=fake.date_time_this_year(),
            exit_datetime=fake.date_time_this_year() if random.choice([True, False]) else None,
            chofer=random.choice(flota_users),
            observations=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
            authorization=random.choice([True, False])
        )
        ingresos.append(ingreso)

    # Poblar Tasks
    tasks = []
    for _ in range(20):
        task = Task.objects.create(
            description=fake.text(max_nb_chars=200),
            urgency=random.choice(['Alta', 'Media', 'Baja']),
            start_datetime=fake.date_time_this_year(),
            end_datetime=fake.date_time_this_year() if random.choice([True, False]) else None,
            service_type=random.choice(service_types),
            supervisor=random.choice([user for user in flota_users if user.role.is_supervisor_role]) if random.choice([True, False]) else None
        )
        tasks.append(task)

    # Poblar TaskAssignments
    task_assignments = []
    for _ in range(30):
        assignment = TaskAssignment.objects.create(
            task=random.choice(tasks),
            user=random.choice(flota_users)
        )
        task_assignments.append(assignment)

    # Poblar Pauses
    for _ in range(10):
        Pause.objects.create(
            assignment=random.choice(task_assignments),
            motivo=fake.sentence(),
            duration=random.randint(10, 120),
            authorization=random.choice([True, False]),
            start_datetime=fake.date_time_this_year(),
            end_datetime=fake.date_time_this_year()
        )

    # Poblar Documents
    for _ in range(15):
        Document.objects.create(
            ingreso=random.choice(ingresos),
            type=random.choice(['Factura', 'Informe', 'Certificado']),
            file_path=f"/documents/{fake.file_name()}",
            upload_datetime=fake.date_time_this_year(),
            user=random.choice(flota_users)
        )

    # Poblar Repuestos
    for _ in range(20):
        Repuesto.objects.create(
            name=fake.word().capitalize(),
            quantity=random.randint(1, 10),
            task=random.choice(tasks) if random.choice([True, False]) else None,
            delivery_datetime=fake.date_time_this_year()
        )

    # Poblar Notifications
    for _ in range(25):
        Notification.objects.create(
            recipient=random.choice(flota_users),
            message=fake.text(max_nb_chars=200),
            sent_datetime=fake.date_time_this_year(),
            type=random.choice(['Alerta', 'Recordatorio', 'Informe'])
        )

    # Poblar Reports
    for _ in range(10):
        Report.objects.create(
            type=random.choice(['Diario', 'Semanal', 'Mensual']),
            generated_datetime=fake.date_time_this_year(),
            data={'data': fake.text(max_nb_chars=200)},
            user=random.choice(flota_users)
        )

    # Poblar MaintenanceSchedules
    for _ in range(15):
        MaintenanceSchedule.objects.create(
            patent=random.choice(vehicles),
            service_type=random.choice(service_types),
            start_datetime=fake.date_time_this_year(),
            recurrence_rule=f"RRULE:FREQ={random.choice(['DAILY', 'WEEKLY', 'MONTHLY'])};COUNT={random.randint(1, 10)}" if random.choice([True, False]) else None,
            reminder_minutes=random.randint(10, 60) if random.choice([True, False]) else None,
            assigned_user=random.choice(flota_users) if random.choice([True, False]) else None,
            supervisor=random.choice([user for user in flota_users if user.role.is_supervisor_role]) if random.choice([True, False]) else None,
            status=random.choice(user_statuses),
            observations=fake.text(max_nb_chars=200) if random.choice([True, False]) else None
        )

    # Poblar WorkOrderStatuses
    work_order_statuses_data = [
        {'name': 'Pendiente', 'description': 'Orden de trabajo pendiente de asignación', 'color': '#ffc107'},
        {'name': 'En Progreso', 'description': 'Orden de trabajo en ejecución', 'color': '#007bff'},
        {'name': 'Completada', 'description': 'Orden de trabajo finalizada', 'color': '#28a745'},
        {'name': 'Cancelada', 'description': 'Orden de trabajo cancelada', 'color': '#dc3545'},
        {'name': 'Pausada', 'description': 'Orden de trabajo temporalmente pausada', 'color': '#6c757d'},
    ]
    
    work_order_statuses = []
    for status_data in work_order_statuses_data:
        status = WorkOrderStatus.objects.create(**status_data)
        work_order_statuses.append(status)

    # Crear órdenes de trabajo para algunos ingresos
    ingresos_for_work_orders = list(Ingreso.objects.all()[:8])  # Usar los primeros 8 ingresos

    for ingreso in ingresos_for_work_orders:
        if not hasattr(ingreso, 'work_order'):  # Solo si no tiene orden de trabajo
            WorkOrder.objects.create(
                ingreso=ingreso,
                status=random.choice(work_order_statuses),
                created_datetime=fake.date_time_this_year(),
                estimated_completion=fake.date_time_this_year() if random.choice([True, False]) else None,
                actual_completion=fake.date_time_this_year() if random.choice([True, False]) else None,
                total_cost=random.uniform(100, 5000)
            )

    # Poblar Incidents
    incidents = []
    for _ in range(20):
        incident = Incident.objects.create(
            vehicle=random.choice(vehicles),
            reported_by=random.choice(flota_users),
            name=fake.sentence(),
            incident_type=random.choice(['Mecanica', 'Electrica', 'Carroceria', 'Neumaticos', 'Otro']),
            description=fake.text(max_nb_chars=300),
            location=fake.address() if random.choice([True, False]) else None,
            latitude=fake.latitude() if random.choice([True, False]) else None,
            longitude=fake.longitude() if random.choice([True, False]) else None,
            is_emergency=random.choice([True, False]),
            requires_tow=random.choice([True, False]),
            priority=random.choice(['Baja', 'Normal', 'Alta', 'Urgente']) if random.choice([True, False]) else None,
            created_by=random.choice(flota_users) if random.choice([True, False]) else None,
            updated_by=random.choice(flota_users) if random.choice([True, False]) else None
        )
        incidents.append(incident)

    print(f"Incidentes poblados: {len(incidents)}")

    # Poblar Reports
    reports = []
    for _ in range(10):
        report = Report.objects.create(
            type=random.choice(['Vehículos', 'Mantenimiento', 'Incidentes', 'Órdenes de Trabajo', 'Repuestos']),
            generated_datetime=fake.date_time_this_year(),
            data={
                'total_records': random.randint(10, 100),
                'period': fake.date_this_year().strftime('%Y-%m'),
                'summary': fake.text(max_nb_chars=200)
            },
            user=random.choice(flota_users)
        )
        reports.append(report)

    print(f"Reportes poblados: {len(reports)}")

    # Poblar WorkOrderMechanics
    work_order_mechanics = []
    mechanics = [user for user in flota_users if user.role.name == 'Mecánico']
    work_orders_list = list(WorkOrder.objects.all())
    if mechanics and work_orders_list:
        for work_order in work_orders_list[:10]:  # Asignar mecánicos a las primeras 10 OT
            mechanic = random.choice(mechanics)
            assignment = WorkOrderMechanic.objects.create(
                work_order=work_order,
                mechanic=mechanic,
                hours_worked=round(random.uniform(1, 8), 2),
                is_active=random.choice([True, False])
            )
            work_order_mechanics.append(assignment)

    print(f"Asignaciones de mecánicos pobladas: {len(work_order_mechanics)}")

    # Poblar SparePartUsages
    spare_part_usages = []
    repuestos_list = list(Repuesto.objects.all())
    if work_orders_list and repuestos_list:
        for work_order in work_orders_list[:15]:  # Usar repuestos en las primeras 15 OT
            repuesto = random.choice(repuestos_list)
            quantity = random.randint(1, 5)
            unit_cost = round(random.uniform(10, 500), 2)
            total_cost = quantity * unit_cost
            usage = SparePartUsage.objects.create(
                work_order=work_order,
                repuesto=repuesto,
                quantity_used=quantity,
                unit_cost=unit_cost,
                total_cost=total_cost,
                notes=fake.text(max_nb_chars=100) if random.choice([True, False]) else None
            )
            spare_part_usages.append(usage)

    print(f"Uso de repuestos poblado: {len(spare_part_usages)}")

    # Poblar Diagnostics
    diagnostics = []
    for incident in incidents[:15]:  # Crear diagnósticos para las primeras 15 incidencias
        diagnostic = Diagnostics.objects.create(
            incident=incident,
            severity=random.choice(['Baja', 'Media', 'Alta', 'Critica']) if random.choice([True, False]) else None,
            category=random.choice(['Seguridad', 'Operativo', 'Mantenimiento']) if random.choice([True, False]) else None,
            symptoms=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
            possible_cause=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
            route=random.choice(routes) if random.choice([True, False]) else None,
            status=random.choice(['Reportada', 'Diagnostico_In_Situ', 'OT_Generada', 'Resuelta']),
            assigned_to=random.choice(mechanics) if mechanics and random.choice([True, False]) else None,
            resolved_at=fake.date_time_this_year() if random.choice([True, False]) else None,
            resolution_notes=fake.text(max_nb_chars=300) if random.choice([True, False]) else None,
            estimated_resolution_time=f"{random.randint(1, 24)} horas" if random.choice([True, False]) else None,
            resolution_type=random.choice(['Taller', 'Campo', 'No_aplica']) if random.choice([True, False]) else None,
            auto_resolved=random.choice([True, False]),
            resolution_source=random.choice(['OT_Completada', 'Ingreso_Cerrado', 'Manual']) if random.choice([True, False]) else None,
            affects_operation=random.choice([True, False]),
            follow_up_required=random.choice([True, False]),
            related_schedule=random.choice(list(MaintenanceSchedule.objects.all())) if MaintenanceSchedule.objects.exists() and random.choice([True, False]) else None,
            related_ingreso=random.choice(ingresos) if random.choice([True, False]) else None,
            related_work_order=random.choice(work_orders_list) if random.choice([True, False]) else None,
            diagnostic_started_at=fake.date_time_this_year() if random.choice([True, False]) else None,
            diagnostic_completed_at=fake.date_time_this_year() if random.choice([True, False]) else None,
            diagnostic_by=random.choice(mechanics) if mechanics and random.choice([True, False]) else None,
            diagnostic_method=random.choice(['Visual', 'Instrumentos', 'Prueba', 'Otro']) if random.choice([True, False]) else None,
            parts_needed=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
            estimated_cost=round(random.uniform(50, 2000), 2) if random.choice([True, False]) else None,
            photos_taken=random.choice([True, False]),
            requires_specialist=random.choice([True, False]),
            environmental_conditions=fake.word() if random.choice([True, False]) else None,
            diagnostics_created_by=random.choice(flota_users) if random.choice([True, False]) else None,
            diagnostics_updated_by=random.choice(flota_users) if random.choice([True, False]) else None
        )
        diagnostics.append(diagnostic)

    print(f"Diagnósticos poblados: {len(diagnostics)}")

    # Poblar IncidentImages
    incident_images = []
    for incident in incidents[:10]:  # Agregar imágenes a las primeras 10 incidencias
        for _ in range(random.randint(1, 3)):  # 1-3 imágenes por incidencia
            image = IncidentImage.objects.create(
                incident=incident,
                name=fake.word().capitalize(),
                image=f"incident_images/{fake.file_name(extension='jpg')}"
            )
            incident_images.append(image)

    print(f"Imágenes de incidentes pobladas: {len(incident_images)}")

    # Poblar IngresoImages
    ingreso_images = []
    for ingreso in ingresos[:10]:  # Agregar imágenes a los primeros 10 ingresos
        for _ in range(random.randint(1, 3)):  # 1-3 imágenes por ingreso
            image = IngresoImage.objects.create(
                ingreso=ingreso,
                name=fake.word().capitalize(),
                image=f"ingreso_images/{fake.file_name(extension='jpg')}",
                uploaded_by=random.choice(flota_users) if random.choice([True, False]) else None
            )
            ingreso_images.append(image)

    print(f"Imágenes de ingresos pobladas: {len(ingreso_images)}")

    print("Base de datos poblada con éxito.")

if __name__ == "__main__":
    populate_db()