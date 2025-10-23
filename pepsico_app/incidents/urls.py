from django.urls import path
from . import views

urlpatterns = [
    path('chofer/report/', views.chofer_report_incident, name='chofer_report_incident'),
    path('guardia/report/', views.guardia_report_incident, name='guardia_report_incident'),
    path('recepcionista/ot/<int:incident_id>/', views.recepcionista_generate_ot, name='recepcionista_generate_ot'),
    path('supervisor/edit/<int:incident_id>/', views.supervisor_edit_incident, name='supervisor_edit_incident'),
    path('list/', views.incident_list, name='incident_list'),
    path('detail/<int:incident_id>/', views.incident_detail, name='incident_detail'),
]