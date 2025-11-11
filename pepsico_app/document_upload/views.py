from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, F, Sum, Avg
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.paginator import Paginator
from django import forms
from django.db import models

from documents.models import Report
from .models import ReportType, UploadedDocument, DocumentType


class DocumentUploadForm(forms.ModelForm):
	"""Formulario para subir documentos."""

	class Meta:
		model = UploadedDocument
		fields = ['title', 'description', 'file', 'document_type']
		widgets = {
			'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del documento'}),
			'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción opcional'}),
			'file': forms.FileInput(attrs={'class': 'form-control'}),
			'document_type': forms.Select(attrs={'class': 'form-control'}),
		}
		labels = {
			'document_type': 'Tipo de documento',
		}


class ReportTypeForm(forms.ModelForm):
	"""Formulario para crear/editar tipos de reporte."""

	class Meta:
		model = ReportType
		fields = ['name', 'active']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del tipo de reporte'}),
			'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
		}


class DocumentTypeForm(forms.ModelForm):
	"""Formulario para crear/editar tipos de documento."""

	class Meta:
		model = DocumentType
		fields = ['name', 'active']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del tipo de documento'}),
			'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
		}


def dashboard(request):
	"""Vista que prepara el contexto para el dashboard integrado de reportes y documentos.

	Calcula métricas tanto de reportes generados como de documentos subidos.
	"""
	now = timezone.now()

	# === MÉTRICAS DE REPORTES ===
	total_reports = Report.objects.count()
	reports_today = Report.objects.filter(generated_datetime__date=now.date()).count()
	reports_last_week = Report.objects.filter(generated_datetime__gte=(now - timedelta(days=7))).count()
	report_types_count = ReportType.objects.filter(active=True).count()

	# Reportes por tipo
	reports_by_type_qs = (
		Report.objects
		.values(type_name=F('type__name'))
		.annotate(count=Count('id_report'))
		.order_by('-count')
	)
	reports_by_type = list(reports_by_type_qs)

	# === MÉTRICAS DE DOCUMENTOS ===
	from .models import UploadedDocument
	total_documents = UploadedDocument.objects.count()
	documents_today = UploadedDocument.objects.filter(uploaded_at__date=now.date()).count()
	documents_last_week = UploadedDocument.objects.filter(uploaded_at__gte=(now - timedelta(days=7))).count()

	# Documentos por tipo
	documents_by_type_qs = (
		UploadedDocument.objects
		.values(type_name=F('document_type__name'))
		.annotate(count=Count('id_document'))
		.order_by('-count')
	)
	documents_by_type = list(documents_by_type_qs)

	# Actividad diaria de reportes (últimos 7 días)
	reports_daily_activity = []
	max_reports_daily = 0
	for i in range(6, -1, -1):
		day = (now - timedelta(days=i)).date()
		count = Report.objects.filter(generated_datetime__date=day).count()
		reports_daily_activity.append({'date': day, 'count': count})
		if count > max_reports_daily:
			max_reports_daily = count

	# Actividad diaria de documentos (últimos 7 días)
	documents_daily_activity = []
	max_documents_daily = 0
	for i in range(6, -1, -1):
		day = (now - timedelta(days=i)).date()
		count = UploadedDocument.objects.filter(uploaded_at__date=day).count()
		documents_daily_activity.append({'date': day, 'count': count})
		if count > max_documents_daily:
			max_documents_daily = count

	# Usuarios más activos en reportes
	top_report_users_qs = (
		Report.objects
		.values(user__name=F('user__name'), user__role__name=F('user__role__name'))
		.annotate(count=Count('id_report'))
		.order_by('-count')[:10]
	)
	top_report_users = list(top_report_users_qs)

	# Usuarios más activos en subida de documentos
	top_upload_users_qs = (
		UploadedDocument.objects
		.values(
			user__name=F('uploaded_by__first_name'),
			user__role=F('uploaded_by__username')  # Using username as role since User model doesn't have role
		)
		.annotate(count=Count('id_document'))
		.order_by('-count')[:10]
	)
	top_upload_users = list(top_upload_users_qs)

	# Reportes y documentos recientes
	recent_reports = Report.objects.select_related('user', 'type').order_by('-generated_datetime')[:5]
	recent_documents = UploadedDocument.objects.select_related('uploaded_by', 'document_type').order_by('-uploaded_at')[:5]

	# Estadísticas de almacenamiento
	total_file_size = UploadedDocument.objects.aggregate(
		total_size=Sum('file_size')
	)['total_size'] or 0
	avg_file_size = UploadedDocument.objects.aggregate(
		avg_size=Avg('file_size')
	)['avg_size'] or 0

	context = {
		# Reportes
		'total_reports': total_reports,
		'reports_today': reports_today,
		'reports_last_week': reports_last_week,
		'report_types_count': report_types_count,
		'reports_by_type': reports_by_type_qs,
		'reports_daily_activity': reports_daily_activity,
		'max_reports_daily': max_reports_daily or 1,
		'top_report_users': top_report_users,
		'recent_reports': recent_reports,

		# Documentos
		'total_documents': total_documents,
		'documents_today': documents_today,
		'documents_last_week': documents_last_week,
		'documents_by_type': documents_by_type,
		'documents_daily_activity': documents_daily_activity,
		'max_documents_daily': max_documents_daily or 1,
		'top_upload_users': top_upload_users,
		'recent_documents': recent_documents,

		# Estadísticas generales
		'total_file_size': total_file_size,
		'avg_file_size': avg_file_size,
		'active_users_reports': Report.objects.values('user').distinct().count(),
		'active_users_uploads': UploadedDocument.objects.values('uploaded_by').distinct().count(),
	}

	return render(request, 'document_upload/dashboard.html', context)


@login_required
def upload_document(request):
	"""Vista para subir un nuevo documento."""
	if request.method == 'POST':
		form = DocumentUploadForm(request.POST, request.FILES)
		if form.is_valid():
			document = form.save(commit=False)
			document.uploaded_by = request.user
			document.save()
			messages.success(request, f'Documento "{document.title}" subido exitosamente.')
			return redirect('document_upload:document_list')
	else:
		form = DocumentUploadForm()

	context = {
		'form': form,
		'document_types': DocumentType.objects.filter(active=True),
	}
	return render(request, 'document_upload/upload.html', context)


@login_required
def document_list(request):
	"""Vista para listar documentos subidos."""
	documents = UploadedDocument.objects.select_related('uploaded_by', 'document_type').all()

	# Filtros
	document_type_filter = request.GET.get('document_type')
	if document_type_filter:
		documents = documents.filter(document_type_id=document_type_filter)

	search_query = request.GET.get('search')
	if search_query:
		documents = documents.filter(
			models.Q(title__icontains=search_query) |
			models.Q(description__icontains=search_query)
		)

	# Paginación
	paginator = Paginator(documents, 20)  # 20 documentos por página
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	context = {
		'page_obj': page_obj,
		'document_types': DocumentType.objects.filter(active=True),
		'current_filters': {
			'document_type': document_type_filter,
			'search': search_query,
		},
	}
	return render(request, 'document_upload/list.html', context)


@login_required
def delete_document(request, document_id):
	"""Vista para eliminar un documento."""
	document = get_object_or_404(UploadedDocument, id_document=document_id)

	# Verificar permisos (solo el propietario puede eliminar)
	if document.uploaded_by != request.user:
		messages.error(request, 'No tienes permisos para eliminar este documento.')
		return redirect('document_upload:document_list')

	if request.method == 'POST':
		document_title = document.title
		document.file.delete()  # Eliminar el archivo del sistema de archivos
		document.delete()
		messages.success(request, f'Documento "{document_title}" eliminado exitosamente.')
		return redirect('document_upload:document_list')

	context = {
		'document': document,
	}
	return render(request, 'document_upload/delete.html', context)


@login_required
def report_type_list(request):
	"""Vista para listar tipos de reporte."""
	report_types = ReportType.objects.all().order_by('name')
	
	context = {
		'report_types': report_types,
		'title': 'Tipos de Reporte',
	}
	return render(request, 'document_upload/report_type_list.html', context)


@login_required
def report_type_create(request):
	"""Vista para crear un nuevo tipo de reporte."""
	if request.method == 'POST':
		form = ReportTypeForm(request.POST)
		if form.is_valid():
			report_type = form.save()
			messages.success(request, f'Tipo de reporte "{report_type.name}" creado exitosamente.')
			return redirect('document_upload:report_type_list')
	else:
		form = ReportTypeForm()
	
	context = {
		'form': form,
		'title': 'Crear Tipo de Reporte',
		'button_text': 'Crear',
	}
	return render(request, 'document_upload/report_type_form.html', context)


@login_required
def report_type_edit(request, type_id):
	"""Vista para editar un tipo de reporte."""
	report_type = get_object_or_404(ReportType, id_type=type_id)
	
	if request.method == 'POST':
		form = ReportTypeForm(request.POST, instance=report_type)
		if form.is_valid():
			report_type = form.save()
			messages.success(request, f'Tipo de reporte "{report_type.name}" actualizado exitosamente.')
			return redirect('document_upload:report_type_list')
	else:
		form = ReportTypeForm(instance=report_type)
	
	context = {
		'form': form,
		'report_type': report_type,
		'title': 'Editar Tipo de Reporte',
		'button_text': 'Actualizar',
	}
	return render(request, 'document_upload/report_type_form.html', context)


@login_required
def report_type_delete(request, type_id):
	"""Vista para eliminar un tipo de reporte."""
	report_type = get_object_or_404(ReportType, id_type=type_id)
	
	# Verificar si el tipo de reporte está siendo usado
	documents_count = UploadedDocument.objects.filter(document_type=report_type).count()
	
	if request.method == 'POST':
		report_type_name = report_type.name
		report_type.delete()
		messages.success(request, f'Tipo de reporte "{report_type_name}" eliminado exitosamente.')
		return redirect('document_upload:report_type_list')
	
	context = {
		'report_type': report_type,
		'documents_count': documents_count,
	}
	return render(request, 'document_upload/report_type_delete.html', context)


# ===== FUNCIONES PARA GESTIONAR TIPOS DE DOCUMENTOS =====

@login_required
def document_type_list(request):
	"""Vista para listar tipos de documento."""
	document_types = DocumentType.objects.all().order_by('name')
	
	context = {
		'document_types': document_types,
		'title': 'Tipos de Documento',
	}
	return render(request, 'document_upload/document_type_list.html', context)


@login_required
def document_type_create(request):
	"""Vista para crear un nuevo tipo de documento."""
	if request.method == 'POST':
		form = DocumentTypeForm(request.POST)
		if form.is_valid():
			document_type = form.save()
			messages.success(request, f'Tipo de documento "{document_type.name}" creado exitosamente.')
			return redirect('document_upload:document_type_list')
	else:
		form = DocumentTypeForm()
	
	context = {
		'form': form,
		'title': 'Crear Tipo de Documento',
		'button_text': 'Crear',
	}
	return render(request, 'document_upload/document_type_form.html', context)


@login_required
def document_type_edit(request, type_id):
	"""Vista para editar un tipo de documento."""
	document_type = get_object_or_404(DocumentType, id_type=type_id)
	
	if request.method == 'POST':
		form = DocumentTypeForm(request.POST, instance=document_type)
		if form.is_valid():
			document_type = form.save()
			messages.success(request, f'Tipo de documento "{document_type.name}" actualizado exitosamente.')
			return redirect('document_upload:document_type_list')
	else:
		form = DocumentTypeForm(instance=document_type)
	
	context = {
		'form': form,
		'document_type': document_type,
		'title': 'Editar Tipo de Documento',
		'button_text': 'Actualizar',
	}
	return render(request, 'document_upload/document_type_form.html', context)


@login_required
def document_type_delete(request, type_id):
	"""Vista para eliminar un tipo de documento."""
	document_type = get_object_or_404(DocumentType, id_type=type_id)
	
	# Verificar si el tipo de documento está siendo usado
	documents_count = UploadedDocument.objects.filter(document_type=document_type).count()
	
	if request.method == 'POST':
		document_type_name = document_type.name
		document_type.delete()
		messages.success(request, f'Tipo de documento "{document_type_name}" eliminado exitosamente.')
		return redirect('document_upload:document_type_list')
	
	context = {
		'document_type': document_type,
		'documents_count': documents_count,
	}
	return render(request, 'document_upload/document_type_delete.html', context)
