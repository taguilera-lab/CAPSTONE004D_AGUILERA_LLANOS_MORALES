from django.urls import path
from . import views

urlpatterns = [
    path('datos/', views.datos, name='datos'),
    path('busqueda-patente/', views.busqueda_patente, name='busqueda_patente'),
    path('datos/formulario/', views.create_form, name='create_form'),
    path('datos/formulario/editar/<str:modelo>/<int:pk>/', views.edit_form, name='edit_form'),
    path('datos/eliminar/', views.eliminar_registros, name='eliminar_registros'),
]