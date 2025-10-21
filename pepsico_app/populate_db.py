import os
import django
import random
from faker import Faker
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pepsico_app.settings')
django.setup()

from documents.models import Site, SAPEquipment, CECO, VehicleType, VehicleStatus, Vehicle, Role, UserStatus, FlotaUser, Route, ServiceType, Ingreso, Task, TaskAssignment, Pause, Document, Repuesto, Notification, Report, MaintenanceSchedule, WorkOrder, WorkOrderStatus

fake = Faker('es_ES')

def populate_db():
    # Limpiar base de datos
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
    for status_name in ['Operativo', 'Estacionado', 'En reparación', 'Fuera de servicio']:
        status = VehicleStatus.objects.create(
            name=status_name,
            description=fake.text(max_nb_chars=200) if random.choice([True, False]) else None
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
            mileage=random.randint(10000, 200000) if random.choice([True, False]) else None,
            site=random.choice(sites),
            operational=random.choice([True, False]),
            backup=random.choice([True, False]),
            out_of_service=random.choice([True, False]),
            type=random.choice(vehicle_types),
            plan=random.choice([True, False]),
            sinister=random.choice([True, False]),
            observations=fake.text(max_nb_chars=200),
            compliance=fake.word(),
            tct=fake.word() if random.choice([True, False]) else None,
            geotab_confirm=random.choice([True, False]),
            auction=random.choice([True, False]),
            status=random.choice(vehicle_statuses) if random.choice([True, False]) else None
        )
        vehicles.append(vehicle)

    # Poblar Role
    roles = []
    for role_name in ['Conductor', 'Supervisor de Taller', 'Administrador', 'Mecánico']:
        role = Role.objects.create(
            name=role_name,
            description=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
            is_supervisor_role=role_name in ['Supervisor de Taller', 'Administrador']
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

    # Poblar FlotaUsers
    flota_users = []
    for _ in range(15):
        user = FlotaUser.objects.create(
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
            end_datetime=fake.date_time_this_year(),
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

    print("Base de datos poblada con éxito.")

if __name__ == "__main__":
    populate_db()