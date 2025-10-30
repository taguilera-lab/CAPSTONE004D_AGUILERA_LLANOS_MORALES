from django import forms
from documents.models import Diagnostics, Incident, Route, FlotaUser

class DiagnosticsForm(forms.ModelForm):
    """Formulario completo para crear y editar diagnósticos"""

    # Campo adicional para seleccionar múltiples incidentes
    incidents = forms.ModelMultipleChoiceField(
        queryset=Incident.objects.select_related('vehicle').all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '5'
        }),
        label="Incidentes Relacionados",
        help_text="Mantén presionada la tecla Ctrl (o Cmd en Mac) para seleccionar múltiples incidentes"
    )

    class Meta:
        model = Diagnostics
        fields = [
            'severity', 'category', 'symptoms', 'possible_cause',
            'route', 'location', 'status', 'assigned_to', 'diagnostic_method',
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
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación del diagnóstico (ej: Taller Central, Ruta 5 km 45, etc.)'
            }),
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
            'location': 'Ubicación del Diagnóstico',
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
        user = kwargs.pop('user', None)
        incident_id = kwargs.pop('incident_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar solo usuarios con rol de mecánico
        self.fields['assigned_to'].queryset = FlotaUser.objects.filter(role__name='Mecánico')
        
        # Determinar el vehículo para filtrar rutas
        vehicle_for_route = None
        
        # Configurar el queryset del campo incidents según el contexto
        if self.instance and self.instance.pk:
            # Si es un diagnóstico existente, mostrar solo los incidentes asociados
            self.fields['incidents'].queryset = self.instance.incidents.all().select_related('vehicle', 'reported_by').order_by('-reported_at')
            
            # Para rutas: si hay incidentes, usar el vehículo del primer incidente
            incidents = list(self.instance.incidents.all())
            if incidents:
                vehicle_for_route = incidents[0].vehicle
            elif self.instance.diagnostics_created_by:
                # Si es in situ, usar el vehículo del creador
                vehicle_for_route = self.instance.diagnostics_created_by.patent
        else:
            # Si es un nuevo diagnóstico, mostrar todos los incidentes disponibles
            self.fields['incidents'].queryset = Incident.objects.select_related('vehicle', 'reported_by').order_by('-reported_at')
            
            # Para rutas en creación nueva: si es in situ (status inicial es Diagnostico_In_Situ), usar vehículo del usuario
            if self.initial.get('status') == 'Diagnostico_In_Situ' and user and hasattr(user, 'flotauser'):
                vehicle_for_route = user.flotauser.patent
        
        # Filtrar rutas según el vehículo determinado
        if vehicle_for_route:
            # Mostrar solo las rutas activas asociadas al vehículo
            # Una ruta es activa si tiene al menos un vehículo con conductor activo
            self.fields['route'].queryset = vehicle_for_route.routes.filter(
                vehicles__flotauser__status__name='Activo'
            ).distinct()
        else:
            # Si no hay vehículo determinado, mostrar todas las rutas activas
            self.fields['route'].queryset = Route.objects.filter(
                vehicles__flotauser__status__name='Activo'
            ).distinct()
        
        self.fields['incidents'].label_from_instance = lambda obj: f"#{obj.id_incident} - {obj.vehicle.patent} - {obj.name[:30]}"

        # Pre-poblar incidente si se proporciona incident_id
        if incident_id:
            try:
                incident = Incident.objects.get(id_incident=incident_id)
                self.fields['incidents'].initial = [incident]
            except Incident.DoesNotExist:
                pass

        # Hacer algunos campos opcionales según el estado
        if self.instance and self.instance.pk:
            # Si ya existe el diagnóstico, mostrar incidentes actuales
            self.fields['incidents'].initial = list(self.instance.incidents.all())
            
            # Lógica especial para Jefes de taller: assigned_to es obligatorio si el diagnóstico no está asignado
            if user and hasattr(user, 'flotauser') and user.flotauser.role.name == 'Jefe de taller':
                if not self.instance.assigned_to:
                    # Jefe de taller completando diagnóstico pendiente - solo asignación y estado son obligatorios
                    self.fields['assigned_to'].required = True
                    self.fields['assigned_to'].help_text = "Debe asignar este diagnóstico a un mecánico para completarlo."
                    
                    # Hacer opcionales los campos de evaluación técnica y resolución
                    self.fields['severity'].required = False
                    self.fields['category'].required = False
                    self.fields['symptoms'].required = False
                    self.fields['possible_cause'].required = False
                    self.fields['diagnostic_method'].required = False
                    self.fields['resolution_notes'].required = False
                    self.fields['estimated_resolution_time'].required = False
                    self.fields['resolution_type'].required = False
                    self.fields['affects_operation'].required = False
                    self.fields['follow_up_required'].required = False
        else:
            # Para nuevos diagnósticos, algunos campos son opcionales inicialmente
            self.fields['resolution_notes'].required = False
            self.fields['estimated_resolution_time'].required = False
            self.fields['resolution_type'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            # Guardar la relación ManyToMany con incidentes
            if self.cleaned_data.get('incidents'):
                instance.incidents.set(self.cleaned_data['incidents'])
            else:
                instance.incidents.clear()
        
        return instance