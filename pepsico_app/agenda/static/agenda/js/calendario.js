document.addEventListener('DOMContentLoaded', function() {
  console.log('JS cargado, eventsData:', eventsData);
  var calendarEl = document.getElementById('calendar');
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: 'es',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    events: eventsData,
    eventClick: function(info) {
      console.log('Evento clicado:', info.event);
      // Poblar el modal con los datos del evento
      document.getElementById('modal-id').textContent = info.event.id;
      document.getElementById('modal-patent').textContent = info.event.extendedProps.patent;
      document.getElementById('modal-start').textContent = info.event.start ? info.event.start.toLocaleString('es-ES') : '';
      document.getElementById('modal-assigned').textContent = info.event.extendedProps.assigned_user;
      document.getElementById('modal-status').textContent = info.event.extendedProps.status;
      document.getElementById('modal-description').textContent = info.event.extendedProps.description;

      // Poblar incidentes relacionados
      var incidentsList = document.getElementById('modal-incidents-list');
      var incidentsSection = document.getElementById('modal-incidents-section');
      var relatedIncidents = info.event.extendedProps.related_incidents || [];

      if (relatedIncidents.length > 0) {
        var incidentsHtml = '<div class="incidents-list">';
        relatedIncidents.forEach(function(incident) {
          var emergencyClass = incident.is_emergency ? 'text-danger' : '';
          var priorityBadge = incident.priority === 'Alta' ? 
            '<span class="badge bg-danger">Alta</span>' : 
            '<span class="badge bg-warning text-dark">' + incident.priority + '</span>';
          
          incidentsHtml += `
            <div class="incident-item mb-2 p-2 border rounded ${emergencyClass}">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <strong>${incident.name}</strong>
                  <br>
                  <small class="text-muted">${incident.type} • Reportado: ${incident.reported_at}</small>
                </div>
                <div>
                  ${priorityBadge}
                </div>
              </div>
              <p class="mb-0 mt-1 small">${incident.description}</p>
            </div>
          `;
        });
        incidentsHtml += '</div>';
        incidentsList.innerHTML = incidentsHtml;
        incidentsSection.style.display = 'block';
      } else {
        incidentsList.innerHTML = '<p class="text-muted">No hay incidentes relacionados</p>';
        incidentsSection.style.display = 'block';
      }

      // Mostrar el modal con Bootstrap
      var modal = new bootstrap.Modal(document.getElementById('eventModal'));
      modal.show();
      
      // Configurar los botones basado en si ya tiene ingreso
      var hasIngreso = info.event.extendedProps.has_ingreso;
      var createBtn = document.getElementById('create-ingreso-btn');
      var completedBtn = document.getElementById('ingreso-completed-btn');
      
      if (hasIngreso) {
        // Ya tiene ingreso - mostrar botón verde y ocultar crear ingreso
        createBtn.style.display = 'none';
        completedBtn.style.display = 'inline-block';
      } else {
        // No tiene ingreso - mostrar botón crear ingreso y ocultar botón verde
        createBtn.style.display = 'inline-block';
        completedBtn.style.display = 'none';
        
        // Configurar el botón de crear ingreso
        createBtn.onclick = function() {
          var patent = info.event.extendedProps.patent;
          window.location.href = createIngresoUrl + '?patent=' + encodeURIComponent(patent);
        };
      }
    },
    dateClick: function(info) {
      console.log('Día clicado:', info.dateStr);
      calendar.changeView('timeGridDay', info.dateStr);
    }
  });
  calendar.render();
});