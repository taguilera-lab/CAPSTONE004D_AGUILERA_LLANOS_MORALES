from django import forms
from documents.models import Incident, IncidentImage

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'vehicle', 'name', 'incident_type', 'severity', 'category', 'description',
            'symptoms', 'possible_cause', 'location', 'latitude', 'longitude', 'route',
            'status', 'priority', 'assigned_to', 'resolution_notes', 'estimated_resolution_time',
            'is_emergency', 'requires_tow', 'affects_operation', 'follow_up_required'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'symptoms': forms.Textarea(attrs={'rows': 2}),
            'possible_cause': forms.Textarea(attrs={'rows': 2}),
            'resolution_notes': forms.Textarea(attrs={'rows': 3}),
        }

class ChoferIncidentForm(IncidentForm):
    class Meta(IncidentForm.Meta):
        fields = ['vehicle', 'description', 'location', 'latitude', 'longitude', 'incident_type']

class GuardiaIncidentForm(IncidentForm):
    class Meta(IncidentForm.Meta):
        fields = [
            'vehicle', 'name', 'incident_type', 'severity', 'category', 'description',
            'symptoms', 'possible_cause', 'location', 'latitude', 'longitude', 'route',
            'priority', 'is_emergency', 'requires_tow', 'affects_operation'
        ]

class RecepcionistaIncidentForm(IncidentForm):
    class Meta(IncidentForm.Meta):
        fields = ['vehicle', 'incident_type', 'severity', 'description', 'requires_tow']

class SupervisorIncidentForm(IncidentForm):
    class Meta(IncidentForm.Meta):
        fields = IncidentForm.Meta.fields  # Todos los campos para edición

class IncidentImageForm(forms.ModelForm):
    class Meta:
        model = IncidentImage
        fields = ['name', 'image']