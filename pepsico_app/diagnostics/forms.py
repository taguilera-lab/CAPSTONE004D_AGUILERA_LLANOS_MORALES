from django import forms
from documents.models import Diagnostics, Incident, Route, FlotaUser, Vehicle

class DiagnosticsForm(forms.ModelForm):
    """Formulario completo para crear y editar diagnósticos"""

    # Campo adicional para seleccionar incidente si no viene por URL
    incident = forms.ModelChoiceField(
        queryset=Incident.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Incidente Relacionado"
    )

    # Campo adicional para buscar por patente
    vehicle_patent = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese patente del vehículo...',
            'id': 'vehicle_patent'
        }),
        label="Buscar por Patente"
    )

    class Meta:
        model = Diagnostics
        fields = [
            'severity', 'category', 'symptoms', 'possible_cause',
            'route', 'status', 'assigned_to', 'diagnostic_method',
            'resolution_notes', 'estimated_resolution_time', 'resolution_type',
            'affects_operation', 'follow_up_required'
        ]
        widgets = {
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa los síntomas observados...'
            }),
            'possible_cause': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Posibles causas del problema...'
            }),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'diagnostic_method': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Notas de resolución...'
            }),
            'estimated_resolution_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2 horas, 1 día, etc.'
            }),
            'resolution_type': forms.Select(attrs={'class': 'form-select'}),
            'affects_operation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'severity': 'Severidad',
            'category': 'Categoría',
            'symptoms': 'Síntomas',
            'possible_cause': 'Causa Posible',
            'route': 'Ruta Asignada',
            'status': 'Estado',
            'assigned_to': 'Asignado a',
            'diagnostic_method': 'Método de Diagnóstico',
            'resolution_notes': 'Notas de Resolución',
            'estimated_resolution_time': 'Tiempo Estimado de Resolución',
            'resolution_type': 'Tipo de Resolución',
            'affects_operation': 'Afecta Operaciones',
            'follow_up_required': 'Requiere Seguimiento',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo usuarios con rol de mecánico
        self.fields['assigned_to'].queryset = FlotaUser.objects.filter(role__name='Mecánico')

        # Hacer algunos campos opcionales según el estado
        if self.instance and self.instance.pk:
            # Si ya existe el diagnóstico, algunos campos pueden ser requeridos
            pass
        else:
            # Para nuevos diagnósticos, algunos campos son opcionales inicialmente
            self.fields['resolution_notes'].required = False
            self.fields['estimated_resolution_time'].required = False
            self.fields['resolution_type'].required = False