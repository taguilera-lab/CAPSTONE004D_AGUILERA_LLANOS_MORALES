from django.urls import path
from . import views

app_name = 'pausas'

urlpatterns = [
    # Dashboard
    path('', views.pauses_dashboard, name='dashboard'),

    # Tipos de Pausa
    path('tipos/', views.pause_type_list, name='pause_type_list'),
    path('tipos/crear/', views.pause_type_create, name='pause_type_create'),
    path('tipos/<str:pk>/', views.pause_type_detail, name='pause_type_detail'),
    path('tipos/<str:pk>/editar/', views.pause_type_update, name='pause_type_update'),
    path('tipos/<str:pk>/desactivar/', views.pause_type_deactivate, name='pause_type_deactivate'),
    path('tipos/<str:pk>/activar/', views.pause_type_activate, name='pause_type_activate'),

    # Pausas en Órdenes de Trabajo
    path('ordenes/', views.work_order_pause_list, name='work_order_pause_list'),
    path('ordenes/crear/', views.work_order_pause_create, name='work_order_pause_create'),
    path('ordenes/<int:pk>/', views.work_order_pause_detail, name='work_order_pause_detail'),
    path('ordenes/<int:pk>/finalizar/', views.work_order_pause_end, name='work_order_pause_end'),
    path('ordenes/<int:pk>/autorizar/', views.work_order_pause_authorize, name='work_order_pause_authorize'),

    # Pausas Rápidas
    path('rapida/', views.quick_pause_create, name='quick_pause_create'),

    # API AJAX
    path('api/mecanicos/', views.ajax_load_mechanics, name='ajax_load_mechanics'),
    path('api/repuestos/', views.ajax_load_spare_parts, name='ajax_load_spare_parts'),
]