from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario, name='calendario'),
    path('ingresos/', views.ingresos_list, name='ingresos_list'),
    path('ingresos/crear/', views.ingreso_create_select, name='ingreso_create_select'),
    path('ingresos/crear/directo/', views.ingreso_create, name='ingreso_create'),
    path('ingresos/<int:pk>/', views.ingreso_detail, name='ingreso_detail'),
    path('ingresos/agendar/', views.agendar_ingreso, name='agendar_ingreso'),
    path('salidas/registrar/', views.registrar_salida, name='registrar_salida'),
]