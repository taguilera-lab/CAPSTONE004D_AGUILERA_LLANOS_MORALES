#!/bin/bash

# Script para cargar todos los fixtures de la aplicación Pepsico
# Uso: ./load_fixtures.sh

echo "Cargando fixtures de la aplicación Pepsico Fleet Management..."
echo "Asegúrate de estar en el directorio raíz del proyecto Django"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "Error: No se encuentra manage.py. Ejecuta este script desde el directorio raíz del proyecto Django."
    exit 1
fi

echo "1/9 Cargando datos básicos (sitios, equipos, tipos, estados)..."
python manage.py loaddata fixtures/01_documents_basic.json

echo "2/9 Cargando usuarios y roles..."
python manage.py loaddata fixtures/02_users.json

echo "3/9 Cargando vehículos..."
python manage.py loaddata fixtures/03_vehicles.json

echo "4/9 Cargando órdenes de trabajo..."
python manage.py loaddata fixtures/04_workorders.json

echo "5/9 Cargando ingresos y mantenimientos..."
python manage.py loaddata fixtures/05_ingresos_maintenance.json

echo "6/9 Cargando incidentes e imágenes..."
python manage.py loaddata fixtures/06_incidents_images.json

echo "7/9 Cargando repuestos..."
python manage.py loaddata fixtures/07_repuestos.json

echo "8/9 Cargando pausas..."
python manage.py loaddata fixtures/08_pausas.json

echo "9/10 Cargando documentos..."
python manage.py loaddata fixtures/09_documents_upload.json

echo "10/10 Cargando usuarios del sistema..."
python manage.py loaddata fixtures/10_auth_users.json

echo ""
echo "¡Todos los fixtures han sido cargados exitosamente!"
echo ""
echo "Resumen de datos cargados:"
echo "- Sitios, equipos SAP, CECO, tipos y estados"
echo "- Usuarios y roles de flota"
echo "- 20 vehículos"
echo "- Órdenes de trabajo y asignaciones"
echo "- Ingresos y programaciones de mantenimiento"
echo "- Incidentes con diagnósticos e imágenes"
echo "- Repuestos, proveedores y movimientos de stock"
echo "- Tipos de pausa y pausas registradas"
echo "- Tipos de documento y documentos subidos"
echo ""
echo "Para verificar que los datos se cargaron correctamente, puedes ejecutar:"
echo "python manage.py shell -c \"from django.apps import apps; [(app.name, sum(model.objects.count() for model in app.get_models())) for app in apps.get_app_configs() if any(model.objects.count() > 0 for model in app.get_models())]\""