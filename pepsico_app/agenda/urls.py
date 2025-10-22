from django.urls import path
from . import views

urlpatterns = [
    path('calendario/', views.calendario, name='calendario'),
    path('ingresos/', views.ingresos_list, name='ingresos_list'),
    path('ingresos/crear/', views.ingreso_create_select, name='ingreso_create_select'),
    path('ingresos/crear/directo/', views.ingreso_create, name='ingreso_create'),
    path('ingresos/crear/confirmar/', views.ingreso_create_from_schedule, name='ingreso_create_from_schedule'),
    path('ingresos/<int:pk>/', views.ingreso_detail, name='ingreso_detail'),
    path('salidas/registrar/', views.registrar_salida, name='registrar_salida'),
    path('calendario/agendar/', views.agendar_ingreso, name='agendar_ingreso'),
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
]