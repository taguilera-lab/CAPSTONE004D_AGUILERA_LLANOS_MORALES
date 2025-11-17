# Sistema de Gestión de Taller y Mantenimiento de Flota - PepsiCo

## Descripción

Este proyecto es un sistema web desarrollado como Capstone para la gestión integral de operaciones de taller y mantenimiento de flota vehicular en PepsiCo. Construido con Django (Python), permite a usuarios con roles específicos (Jefe de Taller, Recepcionista, Guardia, Mecánico, etc.) gestionar ingresos de vehículos, agendas de mantenimiento, incidentes, diagnósticos, órdenes de trabajo, inventario de repuestos, pausas operativas, notificaciones y reportes automáticos.

El sistema optimiza procesos de taller, mejora la trazabilidad de vehículos y proporciona métricas de productividad, con potencial para integración futura con SAP y herramientas de IA.

**Estado del Proyecto**: Completado al 94% (todas las historias de usuario principales implementadas; módulos de notificaciones y control de llaves pendientes para futuras versiones).

## Características Principales

- **Gestión de Ingresos**: Registro de vehículos por patente, ruta y chofer, con subida de imágenes.
- **Agenda de Mantenimiento**: Programación sin solapamientos, con algoritmos de detección de conflictos.
- **Incidentes y Diagnósticos**: Reporte de incidentes en portería, diagnósticos iniciales y control de calidad.
- **Órdenes de Trabajo**: Creación, asignación automática a mecánicos y seguimiento de estado.
- **Inventario de Repuestos**: Gestión de stock, alertas de bajo inventario (sin integración SAP en V1).
- **Pausas Operativas**: Registro de pausas con motivo y autorización.
- **Notificaciones**: Sistema de alertas por correo (pendiente de implementación completa).
- **Reportes y KPIs**: Generación automática de reportes en Excel, exportación a Power BI y dashboards de métricas.
- **Autenticación y Roles**: Control de acceso basado en roles (RBAC) con permisos específicos.
- **Documentos e Imágenes**: Subida y gestión de archivos multimedia con retención de 45 días.

## Tecnologías Utilizadas

- **Backend**: Python 3.x, Django 4.x
- **Base de Datos**: SQLite (para desarrollo; configurable a PostgreSQL/MySQL en producción)
- **Frontend**: HTML5, CSS3, JavaScript (con Bootstrap para responsividad)
- **Herramientas Adicionales**: Git para control de versiones, openpyxl para reportes Excel
- **Metodología**: Scrum (con artefactos como Product Backlog, Velocity Chart, Burndown Chart)

## Instalación

### Prerrequisitos
- Python 3.8 o superior instalado.
- Git para clonar el repositorio.
- (Opcional) Virtualenv para entorno virtual.

### Pasos de Instalación
1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/taguilera-lab/CAPSTONE004D_AGUILERA_LLANOS_MORALES.git
   cd CAPSTONE004D_AGUILERA_LLANOS_MORALES/CAPSTONE/Fase\ 2/Evidencias\ Proyecto/Evidencias\ de\ sistema\ Aplicación\ Base\ de\ Datos
   # En Windows: cd "CAPSTONE004D_AGUILERA_LLANOS_MORALES\CAPSTONE\Fase 2\Evidencias Proyecto\Evidencias de sistema Aplicación Base de Datos"
   ```

2. **Crea y activa un entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura la base de datos**:
   ```bash
   python manage.py migrate
   ```

5. **Carga datos iniciales** (opcional, si hay fixtures):
   ```bash
   python manage.py loaddata initial_data.json  # Si existe
   ```

6. **Ejecuta el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```
   Accede a la aplicación en `http://127.0.0.1:8000/`.

## Uso

1. **Acceso**: Inicia sesión con credenciales de usuario (roles predefinidos en la base de datos).

### Usuarios de Prueba
Para probar la aplicación, usa estos usuarios de ejemplo (creados con fixtures o manualmente). Cada uno tiene permisos según su rol. **Nota**: Estas son credenciales de demostración; en producción, crea usuarios reales.

- **Administrador (Superusuario)**:  
  - Username: `admin`  
  - Password: `admin123`  
  - Acceso: Todos los módulos, gestión de usuarios.

- **Vendedor**:  
  - Username: `vendedor`  
  - Password: `123`  
  - Acceso: Agendas, incidentes.

  - Username: `vendedor2`  
  - Password: `ingenieria1`  
  - Acceso: Agendas, incidentes.

  - Username: `vendedor3`  
  - Password: `ingenieria1`  
  - Acceso: Agendas, incidentes.

- **Jefe de Taller**:  
  - Username: `jefe_de_taller`  
  - Password: `123`  
  - Acceso: Agendas, diagnósticos, órdenes de trabajo, control de calidad.

- **Recepcionista**:  
  - Username: `recepcionista_de_vehículos`  
  - Password: `123`  
  - Acceso: Registro de ingresos, subida de documentos/imágenes.

- **Guardia**:  
  - Username: `guardia`  
  - Password: `123`  
  - Acceso: Reporte de incidentes, autorización de salidas.

- **Mecánico**:  
  - Username: `mecanico`  
  - Password: `123`  
  - Acceso: Diagnósticos, pausas operativas.

- **Supervisor**:  
  - Username: `supervisor`  
  - Password: `123`  
  - Acceso: Asignación de tareas, dashboards de progreso. Reportes, KPIs, exportación a Excel/Power BI

- **Bodeguero**:  
  - Username: `bodeguero`  
  - Password: `123`  
  - Acceso: Gestión de inventario de repuestos.

- **Jefe de Flota**:  
  - Username: `jefe_de_flota`  
  - Password: `123`  
  - Acceso: Notificaciones, estado de vehículos. Reportes, KPIs, exportación a Excel/Power BI

Si no existen estos usuarios, puedes crearlos manualmente en el admin de Django o cargar fixtures.

2. **Navegación**: Usa el menú principal para acceder a módulos según tu rol.
3. **Ejemplos**:
   - Recepcionista: Registra un ingreso de vehículo en "Ingresos".
   - Jefe de Taller: Programa una agenda en "Agenda".
   - Coordinador: Genera un reporte en "Reportes".
4. **Reportes**: Exporta datos a Excel desde la sección de KPIs.

Para más detalles, consulta la documentación de historias de usuario en `CAPSTONE/Fase 2/Evidencias Proyecto/Evidencias de Documentación` o los archivos de artefactos Scrum.

## Estructura del Proyecto

```
pepsico_app/
├── pepsico_app/          # Configuración principal de Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── agenda/               # App de agendas de mantenimiento
├── documents/            # App de gestión de documentos
├── incidents/            # App de incidentes
├── diagnostics/          # App de diagnósticos
├── login/                # App de autenticación
├── media/                # Archivos subidos (imágenes)
├── static/               # Archivos estáticos (CSS, JS)
├── templates/            # Plantillas HTML
├── manage.py             # Script de gestión de Django
└── db.sqlite3            # Base de datos (SQLite)
```

## Contribución

1. Forkea el repositorio.
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`.
3. Realiza commits descriptivos.
4. Envía un Pull Request.

Asegúrate de seguir las guías de estilo de Python (PEP 8) y agregar tests para nuevas funcionalidades.

## Licencia

Este proyecto es de uso académico y no tiene licencia comercial. Para uso en producción, contacta al autor.

## Autor

**Tomás Aguilera**  
- Email: t.aguilera@duoc.cl  
- LinkedIn: https://www.linkedin.com/in/tom%C3%A1s-aguilera-cerda-ab19391ba/  
- GitHub: taguilera-lab (https://github.com/taguilera-lab)

Proyecto desarrollado como parte del Capstone en [DuocUC], 2025.

**Contribuciones**
- **Diseño**: Nicolás Llanos y Michelle Morales, DuocUC Ingeniería Informática

## Notas Adicionales

- **Artefactos Scrum**: Revisa `velocity_chart_tablas.txt`, `burndown_chart_tablas.txt`, `etapas_proyecto_apt.txt` y `reflexion_proyecciones_apt.txt` para documentación completa.
- **Futuras Mejoras**: Integración con SAP, implementación de notificaciones completas, IA para predicciones de mantenimiento.
- **Soporte**: Para issues, abre un ticket en GitHub o contacta al autor.

¡Gracias por revisar el proyecto!
