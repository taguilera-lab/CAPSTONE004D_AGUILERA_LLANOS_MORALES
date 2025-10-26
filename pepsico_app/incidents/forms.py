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
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'reported_by': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la incidencia'}),
            'incident_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción detallada'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'is_emergency': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_tow': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ChoferIncidentForm(IncidentForm):
    class Meta(IncidentForm.Meta):
        fields = ['vehicle', 'description', 'location',
                  'latitude', 'longitude', 'incident_type']


class GuardiaIncidentForm(IncidentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['priority'] = 'Normal'

    class Meta(IncidentForm.Meta):
        fields = ['vehicle', 'description', 'location',
                  'latitude', 'longitude', 'incident_type', 'priority']


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
