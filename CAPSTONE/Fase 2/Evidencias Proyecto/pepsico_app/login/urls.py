from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/jefe-flota/', views.jefe_flota_dashboard, name='jefe_flota_dashboard'),
    path('dashboard/mecanico/', views.mecanico_dashboard, name='mecanico_dashboard'),
    path('dashboard/vendedor/', views.vendedor_dashboard, name='vendedor_dashboard'),
    path('dashboard/guardia/', views.guardia_dashboard, name='guardia_dashboard'),
    path('dashboard/bodeguero/', views.bodeguero_dashboard, name='bodeguero_dashboard'),
    path('dashboard/supervisor/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('dashboard/jefe-taller/', views.jefe_taller_dashboard_detailed, name='jefe_taller_dashboard'),
    path('dashboard/recepcionista/', views.recepcionista_vehiculos_dashboard, name='recepcionista_vehiculos_dashboard'),
]