from django.urls import path
from . import views

app_name = 'diagnostics'

urlpatterns = [
    path('', views.diagnostics_list, name='diagnostics_list'),
    path('crear/', views.diagnostics_create, name='diagnostics_create'),
    path('crear-multiple/', views.diagnostics_create_multiple, name='diagnostics_create_multiple'),
    path('<int:diagnostic_id>/', views.diagnostics_detail, name='diagnostics_detail'),
    path('<int:diagnostic_id>/editar/', views.diagnostics_update, name='diagnostics_update'),
    path('api/incidents/<int:incident_id>/vehicle/', views.get_incident_vehicle_info, name='get_incident_vehicle_info'),
]