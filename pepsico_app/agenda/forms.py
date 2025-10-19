from django import forms
from documents.models import Ingreso, Vehicle, ServiceType, FlotaUser, Route, Site, MaintenanceSchedule, UserStatus

class IngresoForm(forms.ModelForm):
    route = forms.ModelChoiceField(queryset=Route.objects.all(), required=False, label="Ruta")
    site = forms.CharField(disabled=True, required=False, label="Sucursal de Origen")

    class Meta:
        model = Ingreso
        fields = ['patent', 'service_type', 'entry_datetime', 'exit_datetime', 'chofer', 'supervisor', 'observations', 'authorization']
        widgets = {
            'entry_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'exit_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Para edición, poblar site y route
            self.fields['site'].initial = self.instance.patent.site.name if self.instance.patent.site else ''
            self.fields['route'].initial = Route.objects.filter(truck=self.instance.patent).first()
        else:
            # Para creación, deshabilitar hasta seleccionar patent
            self.fields['site'].widget.attrs['readonly'] = True
            self.fields['route'].queryset = Route.objects.none()


class AgendarIngresoForm(forms.ModelForm):

    class Meta:
        model = MaintenanceSchedule
        fields = ['patent', 'start_datetime', 'expected_chofer', 'observations']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extraer el usuario de kwargs
        super().__init__(*args, **kwargs)
        
        # Establecer un estado por defecto
        if not self.instance.pk:
            default_status = UserStatus.objects.filter(name='Programado').first()
            if default_status:
                self.instance.status = default_status
            else:
                self.instance.status = UserStatus.objects.first()
        
        # Pre-llenar el chofer esperado con el usuario actual
        if self.user and not self.instance.pk:  # Solo para nuevos registros
            self.fields['expected_chofer'].initial = self.user
            self.fields['expected_chofer'].widget.attrs['readonly'] = True
            self.fields['expected_chofer'].help_text = "Este campo se registra automáticamente con tu usuario."