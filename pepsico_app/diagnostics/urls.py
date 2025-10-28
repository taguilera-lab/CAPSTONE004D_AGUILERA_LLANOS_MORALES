from django.urls import path
from . import views

app_name = 'diagnostics'

urlpatterns = [
    path('', views.diagnostics_list, name='diagnostics_list'),
    path('crear/', views.diagnostics_create, name='diagnostics_create'),
    path('crear/<int:incident_id>/', views.diagnostics_create, name='diagnostics_create_for_incident'),
    path('<int:diagnostic_id>/', views.diagnostics_detail, name='diagnostics_detail'),
    path('<int:diagnostic_id>/editar/', views.diagnostics_update, name='diagnostics_update'),
]