from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from documents.models import Incident, IncidentImage, WorkOrder, Ingreso
from .forms import ChoferIncidentForm, GuardiaIncidentForm, RecepcionistaIncidentForm, SupervisorIncidentForm, IncidentImageForm

@login_required
def chofer_report_incident(request):
    if request.method == 'POST':
        form = ChoferIncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user.flotauser
            incident.status = 'Reportada'
            incident.save()
            messages.success(request, 'Incidente reportado exitosamente.')
            return redirect('incident_list')
    else:
        form = ChoferIncidentForm()
    return render(request, 'incidents/chofer_report.html', {'form': form})

@login_required
def guardia_report_incident(request):
    if request.method == 'POST':
        form = GuardiaIncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user.flotauser
            incident.status = 'Reportada'
            incident.save()
            messages.success(request, 'Incidente reportado exitosamente.')
            return redirect('incident_list')
    else:
        form = GuardiaIncidentForm()
    return render(request, 'incidents/guardia_report.html', {'form': form})

@login_required
def recepcionista_generate_ot(request, incident_id):
    incident = get_object_or_404(Incident, id_incident=incident_id)
    if request.method == 'POST':
        # Crear OT móvil (sin ingreso)
        work_order = WorkOrder.objects.create(
            ingreso=None,  # OT móvil
            service_type=None,
            status='Pendiente',
            created_by=request.user.flotauser,
            observations=f'OT móvil para incidente #{incident.id_incident}'
        )
        incident.related_work_order = work_order
        incident.save()
        messages.success(request, 'OT de mecánica in situ generada.')
        return redirect('incident_detail', incident_id=incident.id_incident)
    return render(request, 'incidents/recepcionista_ot.html', {'incident': incident})

@login_required
def supervisor_edit_incident(request, incident_id):
    incident = get_object_or_404(Incident, id_incident=incident_id)
    if request.method == 'POST':
        form = SupervisorIncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incidente actualizado.')
            return redirect('incident_detail', incident_id=incident.id_incident)
    else:
        form = SupervisorIncidentForm(instance=incident)
    return render(request, 'incidents/supervisor_edit.html', {'form': form, 'incident': incident})

@login_required
def incident_list(request):
    incidents = Incident.objects.all()  # Filtrar por usuario/rol en producción
    return render(request, 'incidents/incident_list.html', {'incidents': incidents})

@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, id_incident=incident_id)
    return render(request, 'incidents/incident_detail.html', {'incident': incident})
