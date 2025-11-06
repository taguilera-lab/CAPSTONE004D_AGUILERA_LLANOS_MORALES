from django.urls import path
from . import views

urlpatterns = [
    path('calendario/', views.calendario, name='calendario'),
    path('ingresos/', views.ingresos_list, name='ingresos_list'),
    path('ingresos/crear/', views.ingreso_create_select, name='ingreso_create_select'),
    path('ingresos/crear/confirmar/', views.ingreso_create_from_schedule, name='ingreso_create_from_schedule'),
    path('ingresos/<int:pk>/', views.ingreso_detail, name='ingreso_detail'),
    path('salidas/registrar/', views.registrar_salida, name='registrar_salida'),
    path('calendario/agendar/', views.agendar_ingreso, name='agendar_ingreso'),
    path('api/incidents-by-vehicle/', views.get_incidents_by_vehicle, name='get_incidents_by_vehicle'),
    # URLs para órdenes de trabajo
    path('ordenes-trabajo/', views.orden_trabajo_list, name='orden_trabajo_list'),
    path('ordenes-trabajo/crear/<int:ingreso_id>/', views.orden_trabajo_create, name='orden_trabajo_create'),
    path('ordenes-trabajo/<int:work_order_id>/', views.orden_trabajo_detail, name='orden_trabajo_detail'),
    path('ordenes-trabajo/<int:work_order_id>/editar/', views.orden_trabajo_update, name='orden_trabajo_update'),
    path('ordenes-trabajo/<int:work_order_id>/agregar-mecanico/', views.orden_trabajo_add_mechanic, name='orden_trabajo_add_mechanic'),
    path('ordenes-trabajo/<int:work_order_id>/agregar-repuesto/', views.orden_trabajo_add_spare_part, name='orden_trabajo_add_spare_part'),
    path('ordenes-trabajo/<int:work_order_id>/delete-mechanics/', views.orden_trabajo_delete_mechanics, name='orden_trabajo_delete_mechanics'),
    path('ordenes-trabajo/<int:work_order_id>/delete-spare_parts/', views.orden_trabajo_delete_spare_parts, name='orden_trabajo_delete_spare_parts'),
    path('ordenes-trabajo/<int:work_order_id>/completar/', views.orden_trabajo_complete, name='orden_trabajo_complete'),
    path('ordenes-trabajo/<int:work_order_id>/agregar-fotos/', views.orden_trabajo_add_photo, name='orden_trabajo_add_photo'),
    path('ordenes-trabajo/<int:work_order_id>/agregar-tareas-auto/', views.orden_trabajo_add_tasks_auto, name='orden_trabajo_add_tasks_auto'),
    path('ordenes-trabajo/tarea/<int:task_id>/editar/', views.orden_trabajo_edit_task, name='orden_trabajo_edit_task'),
    path('ordenes-trabajo/<int:work_order_id>/asignar-supervisor/', views.orden_trabajo_assign_supervisor, name='orden_trabajo_assign_supervisor'),
    path('ordenes-trabajo/<int:work_order_id>/asignar-tipo-servicio/', views.orden_trabajo_assign_service_type, name='orden_trabajo_assign_service_type'),
    path('schedule/<int:pk>/', views.schedule_detail, name='schedule_detail'),
    path('recepcionista/ingreso-tecnico/', views.recepcionista_ingreso_tecnico, name='recepcionista_ingreso_tecnico'),
    path('api/search-vehicle/', views.search_vehicle_api, name='search_vehicle_api'),
    path('api/search-vehicles/', views.search_vehicles_autocomplete, name='search_vehicles_autocomplete'),
]