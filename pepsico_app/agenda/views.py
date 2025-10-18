from django.shortcuts import render
from documents.models import MaintenanceSchedule
import json

# Create your views here.

def calendario(request):
    schedules = MaintenanceSchedule.objects.all()
    events = []
    for schedule in schedules:
        events.append({
            'id': schedule.id_schedule,
            'title': f"{schedule.patent} - {schedule.service_type.name}",
            'start': schedule.start_datetime.isoformat(),
            'end': schedule.end_datetime.isoformat() if schedule.end_datetime else None,
            'description': schedule.observations or '',
            'patent': str(schedule.patent),
            'service_type': schedule.service_type.name,
            'recurrence_rule': schedule.recurrence_rule or '',
            'reminder_minutes': schedule.reminder_minutes or 0,
            'assigned_user': schedule.assigned_user.name if schedule.assigned_user else '',
            'supervisor': schedule.supervisor.name if schedule.supervisor else '',
            'status': schedule.status.name if schedule.status else '',
        })
    return render(request, 'agenda/calendario.html', {'events': json.dumps(events)})
