from django import forms
from documents.models import Ingreso, Vehicle, ServiceType, FlotaUser, Route, Site, MaintenanceSchedule, UserStatus, WorkOrder, WorkOrderStatus, WorkOrderMechanic, SparePartUsage, Repuesto, Incident

class IngresoForm(forms.ModelForm):
    route = forms.ModelChoiceField(queryset=Route.objects.all(), required=False, label="Ruta")
    site = forms.CharField(disabled=True, required=False, label="Sucursal de Origen")

    class Meta:
        model = Ingreso
        fields = ['patent', 'entry_datetime', 'chofer', 'observations']
        widgets = {
            'entry_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer que chofer sea obligatorio para ingresos directos
        self.fields['chofer'].required = True
        self.fields['chofer'].help_text = "Selecciona el chofer asignado para este ingreso."
        
        # Hacer que observations sea opcional
        self.fields['observations'].required = False
        
        if self.instance and self.instance.pk:
            # Para edición, poblar site y route
            self.fields['site'].initial = self.instance.patent.site.name if self.instance.patent.site else ''
            self.fields['route'].initial = Route.objects.filter(vehicles=self.instance.patent).first()
        else:
            # Para creación, deshabilitar hasta seleccionar patent
            self.fields['site'].widget.attrs['readonly'] = True
            self.fields['route'].queryset = Route.objects.none()


class AgendarIngresoForm(forms.ModelForm):
    # Campo para seleccionar incidentes relacionados
    related_incidents = forms.ModelMultipleChoiceField(
        queryset=Incident.objects.none(),  # Se poblará dinámicamente basado en el vehículo
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '5',  # Mostrar 5 opciones a la vez
        }),
        label="Incidentes Relacionados",
        help_text="Selecciona los incidentes que se resolverán en este mantenimiento (opcional)"
    )

    class Meta:
        model = MaintenanceSchedule
        fields = ['patent', 'start_datetime', 'expected_chofer', 'observations', 'status']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extraer el usuario de kwargs
        super().__init__(*args, **kwargs)
        
        # Configurar el queryset para el campo status
        self.fields['status'].queryset = UserStatus.objects.all()
        
        # Configurar incidentes relacionados
        if self.instance.pk:
            # Si estamos editando, mostrar todos los incidentes del vehículo
            if self.instance.patent:
                self.fields['related_incidents'].queryset = Incident.objects.filter(
                    vehicle=self.instance.patent
                ).order_by('-reported_at')
                # Pre-seleccionar incidentes ya relacionados
                self.fields['related_incidents'].initial = self.instance.related_incidents.all()
        else:
            # Para nuevos registros, incluir todos los incidentes (se filtrarán en JavaScript)
            self.fields['related_incidents'].queryset = Incident.objects.all().order_by('-reported_at')
        
        # Establecer un estado por defecto
        if not self.instance.pk:
            default_status = UserStatus.objects.filter(name='Activo').first()
            if default_status:
                self.fields['status'].initial = default_status
        
        # Pre-llenar el chofer esperado con el usuario actual
        if self.user and not self.instance.pk:  # Solo para nuevos registros
            if hasattr(self.user, 'flotauser'):
                self.fields['expected_chofer'].initial = self.user.flotauser
                self.fields['expected_chofer'].widget.attrs['readonly'] = True
                self.fields['expected_chofer'].help_text = "Este campo se registra automáticamente con tu usuario."

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asignar automáticamente el usuario que crea el agendamiento como assigned_user
        if self.user and not instance.pk:  # Solo para nuevos registros
            if hasattr(self.user, 'flotauser'):
                instance.assigned_user = self.user.flotauser
        
        if commit:
            instance.save()
            # Guardar los incidentes relacionados
            related_incidents = self.cleaned_data.get('related_incidents')
            if related_incidents:
                instance.related_incidents.set(related_incidents)
        
        return instance


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['service_type', 'status', 'estimated_completion', 'observations', 'parts_issued', 'supervisor']
        widgets = {
            'estimated_completion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'observations': forms.Textarea(attrs={'rows': 3}),
            'parts_issued': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo usuarios con roles de supervisor
        self.fields['supervisor'].queryset = FlotaUser.objects.filter(role__is_supervisor_role=True)

        # Configurar opciones de estado según si es creación o edición
        if self.instance.pk:
            # Edición: mostrar todos los estados
            self.fields['status'].queryset = WorkOrderStatus.objects.all()
        else:
            # Creación: solo mostrar "Pendiente" y "En Progreso"
            self.fields['status'].queryset = WorkOrderStatus.objects.filter(
                name__in=['Pendiente', 'En Progreso']
            )
            # Establecer "Pendiente" como valor inicial
            try:
                pending_status = WorkOrderStatus.objects.get(name='Pendiente')
                self.fields['status'].initial = pending_status
            except WorkOrderStatus.DoesNotExist:
                pass


class WorkOrderMechanicForm(forms.ModelForm):
    class Meta:
        model = WorkOrderMechanic
        fields = ['mechanic', 'hours_worked']
        widgets = {
            'hours_worked': forms.NumberInput(attrs={'step': '0.25', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo usuarios con roles de mecánico (no supervisores)
        self.fields['mechanic'].queryset = FlotaUser.objects.filter(role__is_supervisor_role=False)


class SparePartUsageForm(forms.ModelForm):
    class Meta:
        model = SparePartUsage
        fields = ['repuesto', 'quantity_used', 'notes']
        widgets = {
            'quantity_used': forms.NumberInput(attrs={'min': '1'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar repuestos disponibles (quantity > 0)
        self.fields['repuesto'].queryset = Repuesto.objects.filter(quantity__gt=0)