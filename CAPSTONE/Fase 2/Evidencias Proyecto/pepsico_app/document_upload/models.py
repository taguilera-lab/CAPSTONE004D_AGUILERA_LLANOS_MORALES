from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Models to back the `document_upload` dashboard template.
class ReportType(models.Model):
	"""Tipo de reporte (por ejemplo: Inspección, Incidente, Mantenimiento)."""
	id_type = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	class Meta:
		db_table = 'report_types'


class DocumentType(models.Model):
	"""Tipo de documento (por ejemplo: Factura, Contrato, Manual, etc.)."""
	id_type = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	class Meta:
		db_table = 'document_types'


class UploadedDocument(models.Model):
	"""Documento subido por un usuario del sistema."""
	id_document = models.AutoField(primary_key=True)
	title = models.CharField(max_length=200, help_text="Título descriptivo del documento")
	description = models.TextField(blank=True, help_text="Descripción opcional del documento")
	file = models.FileField(upload_to='documents/%Y/%m/%d/', help_text="Archivo a subir")
	file_size = models.PositiveIntegerField(null=True, blank=True, help_text="Tamaño del archivo en bytes")
	file_type = models.CharField(max_length=100, null=True, blank=True, help_text="Tipo MIME del archivo")
	uploaded_at = models.DateTimeField(auto_now_add=True)
	uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
	document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True, help_text="Tipo de documento")

	def __str__(self):
		return f"{self.title} - {self.uploaded_by.username}"

	def save(self, *args, **kwargs):
		# Calcular el tamaño del archivo si no está establecido
		if self.file and not self.file_size:
			self.file_size = self.file.size
		# Obtener el tipo MIME si no está establecido
		if self.file and not self.file_type:
			import mimetypes
			self.file_type = mimetypes.guess_type(self.file.name)[0] or 'application/octet-stream'
		super().save(*args, **kwargs)

	class Meta:
		db_table = 'uploaded_documents'
		ordering = ['-uploaded_at']
