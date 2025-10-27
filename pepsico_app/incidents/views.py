from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from documents.models import Incident, IncidentImage, WorkOrder, Ingreso, Diagnostics
from .forms import ChoferIncidentForm, GuardiaIncidentForm, RecepcionistaIncidentForm, SupervisorIncidentForm, IncidentImageForm

@login_required
def chofer_report_incident(request):
    if request.method == 'POST':
        form = ChoferIncidentForm(request.POST)
        image_form = IncidentImageForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user.flotauser
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
    # Obtener la patente y el ID del ingreso del parámetro GET si existen
    patent = request.GET.get('patent')
    ingreso_id = request.GET.get('ingreso_id')
    initial_data = {}
    related_ingreso = None
    
    if patent:
        try:
            from documents.models import Vehicle, Ingreso
            vehicle = Vehicle.objects.get(patent=patent)
            initial_data['vehicle'] = vehicle
            
            # Si se proporcionó un ID de ingreso específico, usarlo
            if ingreso_id:
                related_ingreso = Ingreso.objects.get(id_ingreso=ingreso_id)
            # Si no se proporcionó ingreso_id, no asociar con ningún ingreso específico
            # (solo prepoblar el vehículo)
            
        except (Vehicle.DoesNotExist, Ingreso.DoesNotExist):
            messages.warning(request, f'No se encontró el vehículo o ingreso especificado')
    
    if request.method == 'POST':
        form = GuardiaIncidentForm(request.POST)
        image_form = IncidentImageForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user.flotauser
            # Asignar el ingreso relacionado si existe
            if related_ingreso:
                incident.related_ingreso = related_ingreso
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
            # Redirigir según el origen: si vino con patent (desde lista de ingresos), volver a lista de ingresos
            patent = request.GET.get('patent')  # El parámetro patent sigue disponible en POST
            if patent:
                return redirect('ingresos_list')
            else:
                return redirect('incident_list')
    else:
        form = GuardiaIncidentForm(initial=initial_data)
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
        
        # Actualizar el estado del diagnóstico a "OT Generada"
        diagnostic, created = Diagnostics.objects.get_or_create(
            incident=incident,
            defaults={
                'status': 'OT_Generada',
                'assigned_to': request.user.flotauser,
                'related_work_order': work_order
            }
        )
        if not created:
            diagnostic.status = 'OT_Generada'
            diagnostic.related_work_order = work_order
            diagnostic.save()
        
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
            incidents = Incident.objects.filter(reported_by=request.user.flotauser).select_related('reported_by__role', 'vehicle').prefetch_related(
                Prefetch('diagnostics', queryset=Diagnostics.objects.order_by('-diagnostics_created_at'), to_attr='latest_diagnostic')
            )
        elif request.user.flotauser.role.name == 'Bodeguero':
            # Bodeguero no puede acceder a incidencias
            incidents = Incident.objects.none()
        else:
            # Otros roles ven todas las incidencias
            incidents = Incident.objects.all().select_related('reported_by__role', 'vehicle').prefetch_related(
                Prefetch('diagnostics', queryset=Diagnostics.objects.order_by('-diagnostics_created_at'), to_attr='latest_diagnostic')
            )
    else:
        # Usuario sin rol asignado, no mostrar incidencias
        incidents = Incident.objects.none()

    return render(request, 'incidents/incident_list.html', {'incidents': incidents})

@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(
        Incident.objects.select_related('reported_by__role', 'vehicle').prefetch_related(
            Prefetch('diagnostics', queryset=Diagnostics.objects.order_by('-diagnostics_created_at'), to_attr='latest_diagnostic')
        ), 
        id_incident=incident_id
    )
    return render(request, 'incidents/incident_detail.html', {'incident': incident})

@login_required
def mechanic_diagnose_incident(request, incident_id):
    """Vista para que un mecánico realice diagnóstico in situ"""
    incident = get_object_or_404(Incident, id_incident=incident_id)
    
    # Verificar que el usuario sea mecánico
    if not (hasattr(request.user, 'flotauser') and request.user.flotauser.role.name == 'Mecánico'):
        messages.error(request, 'Solo los mecánicos pueden realizar diagnósticos.')
        return redirect('incident_detail', incident_id=incident.id_incident)
    
    if request.method == 'POST':
        # Crear o actualizar diagnóstico
        diagnostic, created = Diagnostics.objects.get_or_create(
            incident=incident,
            defaults={
                'status': 'Diagnostico_Mecanica_In_Situ',
                'diagnostic_by': request.user.flotauser,
                'diagnostic_started_at': request.POST.get('diagnostic_started_at'),
                'diagnostic_method': request.POST.get('diagnostic_method'),
                'symptoms': request.POST.get('symptoms'),
                'possible_cause': request.POST.get('possible_cause'),
                'parts_needed': request.POST.get('parts_needed'),
                'estimated_cost': request.POST.get('estimated_cost'),
                'assigned_to': request.user.flotauser
            }
        )
        
        if not created:
            # Actualizar diagnóstico existente
            diagnostic.status = 'Diagnostico_Mecanica_In_Situ'
            diagnostic.diagnostic_by = request.user.flotauser
            diagnostic.diagnostic_started_at = request.POST.get('diagnostic_started_at')
            diagnostic.diagnostic_method = request.POST.get('diagnostic_method')
            diagnostic.symptoms = request.POST.get('symptoms')
            diagnostic.possible_cause = request.POST.get('possible_cause')
            diagnostic.parts_needed = request.POST.get('parts_needed')
            diagnostic.estimated_cost = request.POST.get('estimated_cost')
            diagnostic.save()
        
        messages.success(request, 'Diagnóstico realizado exitosamente.')
        return redirect('incident_detail', incident_id=incident.id_incident)
    
    return render(request, 'incidents/mechanic_diagnose.html', {'incident': incident})

@login_required
def resolve_incident(request, incident_id):
    """Vista para marcar un incidente como resuelto"""
    incident = get_object_or_404(Incident, id_incident=incident_id)
    
    if request.method == 'POST':
        # Obtener o crear diagnóstico
        diagnostic, created = Diagnostics.objects.get_or_create(
            incident=incident,
            defaults={'status': 'Resuelta'}
        )
        
        if not created:
            diagnostic.status = 'Resuelta'
            diagnostic.resolved_at = request.POST.get('resolved_at')
            diagnostic.resolution_notes = request.POST.get('resolution_notes')
            diagnostic.resolution_type = request.POST.get('resolution_type')
            diagnostic.save()
        
        messages.success(request, 'Incidente marcado como resuelto.')
        return redirect('incident_detail', incident_id=incident.id_incident)
    
    return render(request, 'incidents/resolve_incident.html', {'incident': incident})
