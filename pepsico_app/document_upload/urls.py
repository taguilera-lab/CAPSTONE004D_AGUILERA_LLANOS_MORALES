from django.urls import path
from .views import (
    dashboard, upload_document, document_list, delete_document,
    report_type_list, report_type_create, report_type_edit, report_type_delete,
    document_type_list, document_type_create, document_type_edit, document_type_delete,
    reports_dashboard, generate_excel_report
)

app_name = 'document_upload'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('upload/', upload_document, name='upload'),
    path('list/', document_list, name='document_list'),
    path('delete/<int:document_id>/', delete_document, name='delete_document'),
    
    # URLs para gestión de tipos de reporte
    path('report-types/', report_type_list, name='report_type_list'),
    path('report-types/create/', report_type_create, name='report_type_create'),
    path('report-types/edit/<int:type_id>/', report_type_edit, name='report_type_edit'),
    path('report-types/delete/<int:type_id>/', report_type_delete, name='report_type_delete'),
    
    # URLs para gestión de tipos de documento
    path('document-types/', document_type_list, name='document_type_list'),
    path('document-types/create/', document_type_create, name='document_type_create'),
    path('document-types/edit/<int:type_id>/', document_type_edit, name='document_type_edit'),
    path('document-types/delete/<int:type_id>/', document_type_delete, name='document_type_delete'),
    
    # URLs para reportes
    path('reports/', reports_dashboard, name='reports_dashboard'),
    path('reports/generate/<str:report_type>/', generate_excel_report, name='generate_excel_report'),
]
