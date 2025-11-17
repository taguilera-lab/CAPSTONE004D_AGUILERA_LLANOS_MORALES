from django.urls import path
from . import views

urlpatterns = [
    path('', views.datos, name='datos'),
    path('busqueda-patente/', views.busqueda_patente, name='busqueda_patente'),
    path('formulario/', views.create_form, name='create_form'),
    path('formulario/editar/<str:modelo>/<str:pk>/', views.edit_form, name='edit_form'),
    path('eliminar/', views.eliminar_registros, name='eliminar_registros'),
]