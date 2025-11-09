from django import forms
from .models import WorkOrderPause, PauseType
from documents.models import WorkOrder, WorkOrderMechanic, Repuesto
import json

class PauseTypeForm(forms.ModelForm):
    """Formulario para tipos de pausa"""
    class Meta:
        model = PauseType
        fields = ['id_pause_type', 'name', 'description', 'requires_authorization', 'is_active']
        widgets = {
            'id_pause_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID único (ej: BREAK, STOCK)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de pausa'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de pausa'
            }),
            'requires_authorization': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class WorkOrderPauseForm(forms.ModelForm):
    """Formulario para pausas en órdenes de trabajo"""
    # Campos adicionales para fecha y hora separadas
    start_date = forms.DateField(
        label="Fecha de Inicio",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    start_time = forms.TimeField(
        label="Hora de Inicio",
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    notes = forms.CharField(
        required=False,
        label="Notas Adicionales",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notas adicionales sobre la pausa'
        })
    )

    class Meta:
        model = WorkOrderPause
        fields = [
            'work_order', 'mechanic_assignment', 'pause_type', 'reason',
            'affected_spare_part', 'required_quantity', 'available_quantity'
        ]
        widgets = {
            'work_order': forms.Select(attrs={'class': 'form-select'}),
            'mechanic_assignment': forms.Select(attrs={'class': 'form-select'}),
            'pause_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el motivo de la pausa'
            }),
            'affected_spare_part': forms.Select(attrs={'class': 'form-select'}),
            'required_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'available_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar órdenes de trabajo activas (no completadas)
        from documents.models import WorkOrderStatus
        try:
            completed_status = WorkOrderStatus.objects.get(name='Completada')
            self.fields['work_order'].queryset = WorkOrder.objects.exclude(status=completed_status)
        except WorkOrderStatus.DoesNotExist:
            pass

        # Filtrar tipos de pausa activos
        self.fields['pause_type'].queryset = PauseType.objects.filter(is_active=True)

        # Si hay una instancia, inicializar los campos separados
        if self.instance and self.instance.pk and self.instance.start_datetime:
            self.fields['start_date'].initial = self.instance.start_datetime.date()
            self.fields['start_time'].initial = self.instance.start_datetime.time()

        # Si se especifica una work_order, filtrar mechanic_assignments
        if 'work_order' in self.data:
            try:
                work_order_id = int(self.data.get('work_order'))
                self.fields['mechanic_assignment'].queryset = WorkOrderMechanic.objects.filter(
                    work_order_id=work_order_id,
                    is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['mechanic_assignment'].queryset = WorkOrderMechanic.objects.filter(
                work_order=self.instance.work_order,
                is_active=True
            )

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Combinar fecha y hora en start_datetime
        if self.cleaned_data.get('start_date') and self.cleaned_data.get('start_time'):
            from datetime import datetime
            start_datetime = datetime.combine(
                self.cleaned_data['start_date'],
                self.cleaned_data['start_time']
            )
            instance.start_datetime = start_datetime

        # Guardar las notas en el campo reason si no hay reason pero sí hay notes
        if self.cleaned_data.get('notes') and not instance.reason:
            instance.reason = self.cleaned_data['notes']
        elif self.cleaned_data.get('notes') and instance.reason:
            # Agregar las notas al reason existente
            instance.reason += f"\n\nNotas adicionales: {self.cleaned_data['notes']}"

        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        pause_type = cleaned_data.get('pause_type')
        mechanic_assignment = cleaned_data.get('mechanic_assignment')
        
        # Si no es pausa por stock, se requiere mecánico
        if pause_type and pause_type.id_pause_type != 'STOCK' and not mechanic_assignment:
            raise forms.ValidationError(
                'Para este tipo de pausa se requiere seleccionar un mecánico específico. '
                'Solo las pausas por falta de repuestos (STOCK) afectan a todos los mecánicos.'
            )
        
        return cleaned_data


class QuickPauseForm(forms.Form):
    """Formulario rápido para crear pausas comunes"""
    work_order = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control autocomplete-field',
            'placeholder': 'Escriba para buscar orden de trabajo...',
            'autocomplete': 'off',
            'data-field': 'work_order'
        }),
        label="Orden de Trabajo"
    )
    work_order_id = forms.ModelChoiceField(
        queryset=WorkOrder.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )

    mechanic_assignment = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control autocomplete-field',
            'placeholder': 'Escriba para buscar mecánico...',
            'autocomplete': 'off',
            'data-field': 'mechanic'
        }),
        label="Mecánico (opcional)"
    )
    mechanic_id = forms.ModelChoiceField(
        queryset=WorkOrderMechanic.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )

    pause_type = forms.ModelChoiceField(
        queryset=PauseType.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Pausa"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Motivo breve'
        }),
        label="Motivo"
    )
    affected_spare_part = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control autocomplete-field',
            'placeholder': 'Escriba para buscar repuesto...',
            'autocomplete': 'off',
            'data-field': 'spare_part'
        }),
        label="Repuesto Afectado (solo para pausas por stock)"
    )
    spare_part_id = forms.ModelChoiceField(
        queryset=Repuesto.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )

    required_quantity = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        }),
        label="Cantidad Requerida"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurar datos para autocompletado
        from documents.models import WorkOrderStatus, Repuesto
        try:
            completed_status = WorkOrderStatus.objects.get(name='Completada')
            work_orders = WorkOrder.objects.exclude(status=completed_status).order_by('-id_work_order')
        except WorkOrderStatus.DoesNotExist:
            work_orders = WorkOrder.objects.all().order_by('-id_work_order')

        # Agregar datos de órdenes de trabajo al contexto del widget
        work_order_data = []
        for wo in work_orders:
            work_order_data.append({
                'id': wo.id_work_order,
                'text': wo.get_search_display()
            })
        self.fields['work_order'].widget.attrs['data-options'] = json.dumps(work_order_data).replace('"', '&quot;')
        self.fields['work_order_id'].queryset = WorkOrder.objects.filter(id_work_order__in=[item['id'] for item in work_order_data])

        # Agregar datos de mecánicos activos
        mechanics = WorkOrderMechanic.objects.filter(is_active=True).select_related('mechanic').order_by('mechanic__name')
        mechanic_data = []
        for mech in mechanics:
            mechanic_data.append({
                'id': mech.id_assignment,
                'text': mech.get_search_display()
            })
        self.fields['mechanic_assignment'].widget.attrs['data-options'] = json.dumps(mechanic_data).replace('"', '&quot;')
        self.fields['mechanic_id'].queryset = WorkOrderMechanic.objects.filter(id_assignment__in=[item['id'] for item in mechanic_data])

        # Agregar datos de repuestos
        from repuestos.models import SparePartStock
        spare_parts = SparePartStock.objects.filter(current_stock__gt=0).select_related('repuesto').order_by('repuesto__name')
        spare_part_data = []
        for sp in spare_parts:
            spare_part_data.append({
                'id': sp.repuesto.id_repuesto,
                'text': f"{sp.repuesto.name} (Stock: {sp.current_stock})"
            })
        self.fields['affected_spare_part'].widget.attrs['data-options'] = json.dumps(spare_part_data).replace('"', '&quot;')
        self.fields['spare_part_id'].queryset = Repuesto.objects.filter(id_repuesto__in=[item['id'] for item in spare_part_data])

    def clean_work_order_id(self):
        work_order = self.cleaned_data.get('work_order_id')
        if work_order:
            return work_order
        return None

    def clean_mechanic_id(self):
        mechanic = self.cleaned_data.get('mechanic_id')
        if mechanic:
            return mechanic
        return None

    def clean_spare_part_id(self):
        spare_part = self.cleaned_data.get('spare_part_id')
        if spare_part:
            return spare_part
        return None

    def clean(self):
        cleaned_data = super().clean()
        pause_type = cleaned_data.get('pause_type')
        mechanic_id = cleaned_data.get('mechanic_id')
        
        # Si no es pausa por stock, se requiere mecánico
        if pause_type and pause_type.id_pause_type != 'STOCK' and not mechanic_id:
            raise forms.ValidationError(
                'Para este tipo de pausa se requiere seleccionar un mecánico específico. '
                'Solo las pausas por falta de repuestos (STOCK) afectan a todos los mecánicos.'
            )
        
        return cleaned_data