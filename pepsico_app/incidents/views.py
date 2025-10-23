from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from documents.models import Incident, IncidentImage, WorkOrder, Ingreso
from .forms import ChoferIncidentForm, GuardiaIncidentForm, RecepcionistaIncidentForm, SupervisorIncidentForm, IncidentImageForm

@login_required
def chofer_report_incident(request):
    if request.method == 'POST':
        form = ChoferIncidentForm(request.POST)
        image_form = IncidentImageForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user.flotauser
            incident.status = 'Reportada'
            incident.save()

            # Guardar imágenes capturadas desde la cámara
            if request.FILES.getlist('camera_images'):
                for i, image_file in enumerate(request.FILES.getlist('camera_images'), 1):
                    IncidentImage.objects.create(
                        incident=incident,
                        name=f"Foto {i}",
                        image=image_file
                    )

            # También guardar imágenes subidas tradicionalmente si las hay
            if image_form.is_valid() and request.FILES.getlist('images'):
                for i, image_file in enumerate(request.FILES.getlist('images'), len(request.FILES.getlist('camera_images')) + 1):
                    IncidentImage.objects.create(
                        incident=incident,
                        name=f"Imagen {i}",
                        image=image_file
                    )

            messages.success(request, 'Incidente reportado exitosamente.')
            return redirect('incident_list')
    else:
        form = ChoferIncidentForm()
        image_form = IncidentImageForm()
    return render(request, 'incidents/chofer_report.html', {
        'form': form,
        'image_form': image_form
    })

@login_required
def guardia_report_incident(request):
    if request.method == 'POST':
        form = GuardiaIncidentForm(request.POST)
        image_form = IncidentImageForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user.flotauser
            incident.status = 'Reportada'
            incident.save()

            # Guardar imágenes capturadas desde la cámara
            if request.FILES.getlist('camera_images'):
                for i, image_file in enumerate(request.FILES.getlist('camera_images'), 1):
                    IncidentImage.objects.create(
                        incident=incident,
                        name=f"Foto {i}",
                        image=image_file
                    )

            # También guardar imágenes subidas tradicionalmente si las hay
            if image_form.is_valid() and request.FILES.getlist('images'):
                for i, image_file in enumerate(request.FILES.getlist('images'), len(request.FILES.getlist('camera_images')) + 1):
                    IncidentImage.objects.create(
                        incident=incident,
                        name=f"Imagen {i}",
                        image=image_file
                    )

            messages.success(request, 'Incidente reportado exitosamente.')
            return redirect('incident_list')
    else:
        form = GuardiaIncidentForm()
        image_form = IncidentImageForm()
    return render(request, 'incidents/guardia_report.html', {
        'form': form,
        'image_form': image_form
    })

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
        image_form = IncidentImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            # Guardar imágenes adicionales si se subieron
            if image_form.is_valid() and request.FILES.getlist('images'):
                for i, image_file in enumerate(request.FILES.getlist('images'), incident.images.count() + 1):
                    IncidentImage.objects.create(
                        incident=incident,
                        name=f"Imagen {i}",
                        image=image_file
                    )

            messages.success(request, 'Incidente actualizado.')
            return redirect('incident_detail', incident_id=incident.id_incident)
    else:
        form = SupervisorIncidentForm(instance=incident)
        image_form = IncidentImageForm()
    return render(request, 'incidents/supervisor_edit.html', {
        'form': form,
        'incident': incident,
        'image_form': image_form
    })

@login_required
def incident_list(request):
    # Filtrar incidencias según el rol del usuario
    if request.user.is_authenticated and hasattr(request.user, 'flotauser'):
        if request.user.flotauser.role.name == 'Vendedor':
            # Vendedor solo ve las incidencias que él mismo reportó
            incidents = Incident.objects.filter(reported_by=request.user.flotauser)
        elif request.user.flotauser.role.name == 'Bodeguero':
            # Bodeguero no puede acceder a incidencias
            incidents = Incident.objects.none()
        else:
            # Otros roles ven todas las incidencias
            incidents = Incident.objects.all()
    else:
        # Usuario sin rol asignado, no mostrar incidencias
        incidents = Incident.objects.none()

    return render(request, 'incidents/incident_list.html', {'incidents': incidents})

@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, id_incident=incident_id)
    return render(request, 'incidents/incident_detail.html', {'incident': incident})
