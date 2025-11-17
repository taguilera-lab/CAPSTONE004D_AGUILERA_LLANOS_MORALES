# Fixtures de la Aplicación Pepsico Fleet Management

Este directorio contiene fixtures con los datos actuales de la aplicación Django para gestión de flota de Pepsico.

## Archivos de Fixtures

Los fixtures están organizados en orden numérico para facilitar la carga:

1. **01_documents_basic.json** - Datos básicos (sitios, equipos, tipos, estados)
2. **02_users.json** - Usuarios, roles y estados de usuario
3. **03_vehicles.json** - Vehículos de la flota
4. **04_workorders.json** - Órdenes de trabajo y asignaciones
5. **05_ingresos_maintenance.json** - Ingresos de vehículos y programaciones de mantenimiento
6. **06_incidents_images.json** - Incidentes, diagnósticos e imágenes
7. **07_repuestos.json** - Categorías, proveedores, stock y movimientos de repuestos
8. **08_pausas.json** - Tipos de pausa y pausas en órdenes de trabajo
9. **09_documents_upload.json** - Tipos de documento, tipos de reporte y documentos subidos
10. **10_auth_users.json** - Usuarios del sistema Django (auth.User)

## Cómo Cargar los Fixtures

### Opción 1: Usar el script automático

```bash
cd /ruta/a/tu/proyecto/pepsico_app
./fixtures/load_fixtures.sh
```

### Opción 2: Cargar manualmente en orden

```bash
cd /ruta/a/tu/proyecto/pepsico_app
python manage.py loaddata fixtures/01_documents_basic.json
python manage.py loaddata fixtures/02_users.json
python manage.py loaddata fixtures/03_vehicles.json
python manage.py loaddata fixtures/04_workorders.json
python manage.py loaddata fixtures/05_ingresos_maintenance.json
python manage.py loaddata fixtures/06_incidents_images.json
python manage.py loaddata fixtures/07_repuestos.json
python manage.py loaddata fixtures/08_pausas.json
python manage.py loaddata fixtures/09_documents_upload.json
python manage.py loaddata fixtures/10_auth_users.json
```

### Opción 3: Cargar todos de una vez

```bash
python manage.py loaddata fixtures/
```

**Nota**: Al cargar todos de una vez, Django automáticamente ordena las dependencias, pero es más seguro cargar en el orden especificado.

## Contenido de los Datos

### Documents App
- **6 Sitios** (ubicaciones)
- **10 Equipos SAP**
- **5 Centros de Costo (CECO)**
- **5 Tipos de Vehículo**
- **5 Estados de Vehículo**
- **4 Tipos de Servicio**
- **5 Estados de Orden de Trabajo**
- **20 Vehículos**
- **12 Usuarios de Flota**
- **3 Órdenes de Trabajo**
- **4 Asignaciones de Mecánicos**
- **5 Ingresos de Vehículos**
- **40 Programaciones de Mantenimiento**
- **7 Incidentes**
- **3 Diagnósticos**
- **Imágenes**: 7 de incidentes, 26 de ingresos, 2 de órdenes de trabajo

### Repuestos App
- **3 Categorías de Repuestos**
- **1 Proveedor**
- **2 Stocks de Repuestos**
- **7 Movimientos de Stock**
- **2 Órdenes de Compra**
- **2 Items de Órdenes de Compra**

### Pausas App
- **4 Tipos de Pausa**
- **2 Pausas en Órdenes de Trabajo**

### Document Upload App
- **2 Tipos de Documento**
- **8 Tipos de Reporte**
- **3 Documentos Subidos**

## Notas Importantes

1. **Dependencias**: Los fixtures están ordenados para respetar las dependencias de clave foránea.
2. **Archivos Multimedia**: Las imágenes referenciadas en los fixtures pueden no existir en un nuevo entorno.
3. **Usuarios**: Los usuarios tienen contraseñas hasheadas. El usuario admin por defecto puede necesitar recrearse.
4. **Datos Sensibles**: Algunos datos pueden contener información sensible - revisar antes de usar en producción.

## Recrear Fixtures

Para recrear estos fixtures con datos actualizados:

```bash
python manage.py dumpdata [app.Model] --indent 2 > fixtures/nombre_fixture.json
```

Ejemplo:
```bash
python manage.py dumpdata documents.Vehicle --indent 2 > fixtures/vehicles.json
```