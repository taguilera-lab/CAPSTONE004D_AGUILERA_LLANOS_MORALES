#!/usr/bin/env python
"""
Script para poblar datos iniciales de órdenes de trabajo
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/Users/tomi/Documents/CAPSTONE/pepsico-app/pepsico_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pepsico_app.settings')
django.setup()

from documents.models import WorkOrderStatus, FlotaUser, Role

def populate_work_order_statuses():
    """Crear estados iniciales para órdenes de trabajo"""
    statuses = [
        {
            'name': 'Pendiente',
            'description': 'Orden de trabajo creada, esperando asignación de recursos',
            'color': '#ffc107'
        },
        {
            'name': 'En Progreso',
            'description': 'Trabajo en ejecución',
            'color': '#17a2b8'
        },
        {
            'name': 'Completada',
            'description': 'Trabajo finalizado exitosamente',
            'color': '#28a745'
        },
        {
            'name': 'Cancelada',
            'description': 'Trabajo cancelado',
            'color': '#dc3545'
        },
        {
            'name': 'Pausada',
            'description': 'Trabajo temporalmente detenido',
            'color': '#6c757d'
        }
    ]

    created_count = 0
    for status_data in statuses:
        status, created = WorkOrderStatus.objects.get_or_create(
            name=status_data['name'],
            defaults={
                'description': status_data['description'],
                'color': status_data['color']
            }
        )
        if created:
            created_count += 1
            print(f"✓ Creado estado: {status.name}")

    print(f"\nEstados de órdenes de trabajo creados: {created_count}")

def check_roles():
    """Verificar que existan roles de supervisor"""
    supervisor_roles = Role.objects.filter(is_supervisor_role=True)
    mechanic_roles = Role.objects.filter(is_supervisor_role=False)

    print(f"Roles de supervisor encontrados: {supervisor_roles.count()}")
    print(f"Roles de mecánico encontrados: {mechanic_roles.count()}")

    if supervisor_roles.exists():
        print("Roles de supervisor:")
        for role in supervisor_roles:
            print(f"  - {role.name}")
    else:
        print("⚠️ No se encontraron roles de supervisor. Los usuarios con is_supervisor_role=True no podrán ser asignados como supervisores.")

    if mechanic_roles.exists():
        print("Roles de mecánico:")
        for role in mechanic_roles:
            print(f"  - {role.name}")
    else:
        print("⚠️ No se encontraron roles de mecánico. Los usuarios con is_supervisor_role=False podrán ser asignados como mecánicos.")

if __name__ == '__main__':
    print("🚀 Poblando datos iniciales de órdenes de trabajo...")
    print("=" * 50)

    populate_work_order_statuses()
    print()
    check_roles()

    print("\n✅ Proceso completado!")