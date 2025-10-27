from django import forms
from documents.models import Incident, IncidentImage


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'vehicle', 'reported_by', 'name', 'incident_type', 'description',
            'location', 'latitude', 'longitude', 'priority', 'is_emergency', 'requires_tow'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'custom-select'}),
            'reported_by': forms.Select(attrs={'class': 'custom-select'}),
            'name': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Título de la incidencia'}),
            'incident_type': forms.Select(attrs={'class': 'custom-select'}),
            'description': forms.Textarea(attrs={'class': 'custom-textarea', 'rows': 4, 'placeholder': 'Descripción detallada'}),
            'location': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Ubicación'}),
            'latitude': forms.NumberInput(attrs={'class': 'custom-input', 'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'custom-input', 'step': '0.00000001'}),
            'priority': forms.Select(attrs={'class': 'custom-select'}),
            'is_emergency': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
            'requires_tow': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
        }


class ChoferIncidentForm(IncidentForm):
    class Meta(IncidentForm.Meta):
        fields = ['vehicle', 'name', 'incident_type', 'description', 'location',
                  'latitude', 'longitude', 'is_emergency', 'requires_tow']
        labels = {
            'vehicle': 'Vehículo',
            'name': 'Título del incidente',
            'incident_type': 'Tipo de incidente',
            'description': 'Descripción',
            'location': 'Ubicación',
            'latitude': 'Latitud',
            'longitude': 'Longitud',
            'is_emergency': 'Es una emergencia',
            'requires_tow': 'Requiere remolque',
        }


class GuardiaIncidentForm(IncidentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['priority'] = 'Normal'
        # Limitar las opciones de prioridad solo para guardias
        self.fields['priority'].choices = [
            ('Normal', 'Normal'),
            ('Urgente', 'Urgente'),
        ]

    class Meta(IncidentForm.Meta):
        fields = ['vehicle', 'name', 'incident_type', 'description', 'location',
                  'latitude', 'longitude', 'priority', 'is_emergency', 'requires_tow']
        labels = {
            'vehicle': 'Vehículo',
            'name': 'Título del incidente',
            'incident_type': 'Tipo de incidente',
            'description': 'Descripción',
            'location': 'Ubicación',
            'latitude': 'Latitud',
            'longitude': 'Longitud',
            'priority': 'Prioridad',
            'is_emergency': 'Es una emergencia',
            'requires_tow': 'Requiere remolque',
        }


class RecepcionistaIncidentForm(IncidentForm):
    class Meta(IncidentForm.Meta):
        fields = ['vehicle', 'incident_type', 'description', 'requires_tow']


class SupervisorIncidentForm(IncidentForm):
    class Meta(IncidentForm.Meta):
        fields = IncidentForm.Meta.fields  # Todos los campos para edición


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class IncidentImageForm(forms.ModelForm):
    images = forms.FileField(
        required=False,
        widget=MultipleFileInput(
            attrs={'multiple': True, 'accept': 'image/*'}),
        label='Imágenes del incidente',
        help_text='Puede seleccionar múltiples imágenes (JPG, PNG, GIF)'
    )

    class Meta:
        model = IncidentImage
        fields = ['images']
