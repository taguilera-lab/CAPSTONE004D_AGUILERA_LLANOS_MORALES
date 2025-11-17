from django.urls import path
from . import views

app_name = 'repuestos'

urlpatterns = [
    # Dashboard
    path('', views.repuestos_dashboard, name='dashboard'),

    # Categorías
    path('categorias/', views.category_list, name='category_list'),
    path('categorias/crear/', views.category_create, name='category_create'),
    path('categorias/<int:pk>/editar/', views.category_update, name='category_update'),
    path('categorias/<int:pk>/eliminar/', views.category_delete, name='category_delete'),

    # Proveedores
    path('proveedores/', views.supplier_list, name='supplier_list'),
    path('proveedores/crear/', views.supplier_create, name='supplier_create'),
    path('proveedores/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('proveedores/<int:pk>/editar/', views.supplier_update, name='supplier_update'),
    path('proveedores/<int:pk>/eliminar/', views.supplier_delete, name='supplier_delete'),

    # Repuestos
    path('repuestos/', views.spare_part_list, name='spare_part_list'),
    path('repuestos/crear/', views.spare_part_create, name='spare_part_create'),
    path('repuestos/<int:pk>/', views.spare_part_detail, name='spare_part_detail'),
    path('repuestos/<int:pk>/editar/', views.spare_part_update, name='spare_part_update'),
    path('repuestos/<int:pk>/eliminar/', views.spare_part_delete, name='spare_part_delete'),

    # Movimientos de Stock
    path('movimientos/', views.stock_movement_list, name='stock_movement_list'),
    path('movimientos/<int:pk>/', views.stock_movement_detail, name='stock_movement_detail'),
    path('movimientos/crear/', views.stock_movement_create, name='stock_movement_create'),

    # Órdenes de Compra
    path('ordenes-compra/', views.purchase_order_list, name='purchase_order_list'),
    path('ordenes-compra/crear/', views.purchase_order_create, name='purchase_order_create'),
    path('ordenes-compra/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('ordenes-compra/<int:pk>/editar/', views.purchase_order_update, name='purchase_order_update'),
    path('ordenes-compra/<int:pk>/cambiar-estado/', views.purchase_order_change_status, name='purchase_order_change_status'),
    path('ordenes-compra/<int:pk>/actualizar-stock/', views.purchase_order_update_stock_status, name='purchase_order_update_stock_status'),
    path('ordenes-compra/<int:pk>/eliminar/', views.purchase_order_delete, name='purchase_order_delete'),

    # API
    path('api/repuesto/<int:repuesto_id>/stock/', views.get_spare_part_stock, name='get_spare_part_stock'),
]