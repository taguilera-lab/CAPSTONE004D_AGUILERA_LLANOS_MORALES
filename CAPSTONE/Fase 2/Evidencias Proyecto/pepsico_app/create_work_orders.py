#!/usr/bin/env python3
import os
import sys
import django
from datetime import datetime
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pepsico_app.settings')
django.setup()

from documents.models import Ingreso, WorkOrder, WorkOrderStatus, ServiceType

def create_work_orders():
    # Obtener algunos ingresos
    ingresos = list(Ingreso.objects.all()[:5])
    statuses = list(WorkOrderStatus.objects.all())
    service_types = list(ServiceType.objects.all())

    print(f"Encontrados {len(ingresos)} ingresos, {len(statuses)} estados y {len(service_types)} tipos de servicio")

    for i, ingreso in enumerate(ingresos):
        if not hasattr(ingreso, 'work_order'):
            status = random.choice(statuses)
            service_type = random.choice(service_types) if service_types else None
            WorkOrder.objects.create(
                ingreso=ingreso,
                service_type=service_type,
                status=status,
                created_datetime=datetime.now(),
                estimated_completion=datetime.now()
            )
            print(f'Creada OT para ingreso {ingreso.id_ingreso} con status {status.name}')

    print('Órdenes de trabajo totales:', WorkOrder.objects.count())

if __name__ == '__main__':
    create_work_orders()