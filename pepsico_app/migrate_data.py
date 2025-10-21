#!/usr/bin/env python3
"""
Script para migrar datos después de los cambios en el modelo
Ejecutar después de hacer migrate
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pepsico_app.settings')
django.setup()

from documents.models import Task, WorkOrder, ServiceType, Ingreso

def migrate_task_data():
    """Migrar datos de Task después de cambiar ingreso por work_order"""

    print("🔄 Migrando datos de Task...")

    # Obtener el primer service_type disponible como fallback
    default_service_type = ServiceType.objects.first()
    if not default_service_type:
        print("❌ No hay ServiceTypes disponibles. Ejecuta populate_db.py primero.")
        return

    # Migrar Tasks que no tienen work_order asignado
    tasks_without_work_order = Task.objects.filter(work_order__isnull=True)
    print(f"📋 Encontradas {tasks_without_work_order.count()} tasks sin work_order")

    migrated_count = 0
    for task in tasks_without_work_order:
        # Buscar si hay un ingreso relacionado con esta task (por descripción o lógica de negocio)
        # Como no hay relación directa, asignaremos a work_orders existentes
        work_orders = WorkOrder.objects.all()
        if work_orders.exists():
            # Asignar a la primera work_order disponible (lógica simple)
            # En un caso real, aquí iría la lógica de negocio para determinar la relación correcta
            task.work_order = work_orders.first()
            task.service_type = default_service_type
            task.save()
            migrated_count += 1
            print(f"✅ Migrada Task {task.id_task} -> WorkOrder {task.work_order.id_work_order}")

    print(f"📊 Migradas {migrated_count} tasks")

def migrate_work_order_data():
    """Asegurar que todas las WorkOrders tengan service_type"""

    print("🔄 Migrando datos de WorkOrder...")

    # Obtener el primer service_type disponible
    default_service_type = ServiceType.objects.first()
    if not default_service_type:
        print("❌ No hay ServiceTypes disponibles. Ejecuta populate_db.py primero.")
        return

    # Migrar WorkOrders que no tienen service_type
    work_orders_without_service = WorkOrder.objects.filter(service_type__isnull=True)
    print(f"📋 Encontradas {work_orders_without_service.count()} work_orders sin service_type")

    migrated_count = 0
    for work_order in work_orders_without_service:
        work_order.service_type = default_service_type
        work_order.save()
        migrated_count += 1
        print(f"✅ Asignado service_type a WorkOrder {work_order.id_work_order}")

    print(f"📊 Migradas {migrated_count} work_orders")

def validate_migration():
    """Validar que la migración fue exitosa"""

    print("🔍 Validando migración...")

    # Verificar que no hay tasks sin work_order
    tasks_without_work_order = Task.objects.filter(work_order__isnull=True)
    if tasks_without_work_order.exists():
        print(f"⚠️  Aún hay {tasks_without_work_order.count()} tasks sin work_order")
    else:
        print("✅ Todas las tasks tienen work_order asignado")

    # Verificar que no hay work_orders sin service_type
    work_orders_without_service = WorkOrder.objects.filter(service_type__isnull=True)
    if work_orders_without_service.exists():
        print(f"⚠️  Aún hay {work_orders_without_service.count()} work_orders sin service_type")
    else:
        print("✅ Todas las work_orders tienen service_type asignado")

    # Verificar que no hay tasks sin service_type
    tasks_without_service = Task.objects.filter(service_type__isnull=True)
    if tasks_without_service.exists():
        print(f"⚠️  Aún hay {tasks_without_service.count()} tasks sin service_type")
    else:
        print("✅ Todas las tasks tienen service_type asignado")

if __name__ == '__main__':
    print("🚀 Iniciando migración de datos...")
    print("=" * 50)

    try:
        migrate_task_data()
        print()
        migrate_work_order_data()
        print()
        validate_migration()
        print()
        print("✅ Migración de datos completada exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        sys.exit(1)