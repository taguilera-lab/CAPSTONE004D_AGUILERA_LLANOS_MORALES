from django.urls import path
from . import views

urlpatterns = [
    path('chofer/report/', views.chofer_report_incident, name='chofer_report_incident'),
    path('guardia/report/', views.guardia_report_incident, name='guardia_report_incident'),
    path('recepcionista/escalar-mecanica/<int:incident_id>/', views.recepcionista_escalar_mecanica, name='recepcionista_escalar_mecanica'),
    path('supervisor/edit/<int:incident_id>/', views.supervisor_edit_incident, name='supervisor_edit_incident'),
    path('mechanic/diagnose/<int:incident_id>/', views.mechanic_diagnose_incident, name='mechanic_diagnose_incident'),
    path('resolve/<int:incident_id>/', views.resolve_incident, name='resolve_incident'),
    path('list/', views.incident_list, name='incident_list'),
    path('detail/<int:incident_id>/', views.incident_detail, name='incident_detail'),
]