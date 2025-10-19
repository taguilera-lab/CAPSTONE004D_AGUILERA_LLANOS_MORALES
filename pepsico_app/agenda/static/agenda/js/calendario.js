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
      document.getElementById('modal-service-type').textContent = info.event.extendedProps.service_type;
      document.getElementById('modal-start').textContent = info.event.start ? info.event.start.toLocaleString('es-ES') : '';
      document.getElementById('modal-end').textContent = info.event.end ? info.event.end.toLocaleString('es-ES') : '';
      document.getElementById('modal-recurrence').textContent = info.event.extendedProps.recurrence_rule;
      document.getElementById('modal-reminder').textContent = info.event.extendedProps.reminder_minutes;
      document.getElementById('modal-assigned').textContent = info.event.extendedProps.assigned_user;
      document.getElementById('modal-supervisor').textContent = info.event.extendedProps.supervisor;
      document.getElementById('modal-status').textContent = info.event.extendedProps.status;
      document.getElementById('modal-description').textContent = info.event.extendedProps.description;

      // Mostrar el modal con Bootstrap
      var modal = new bootstrap.Modal(document.getElementById('eventModal'));
      modal.show();
      
      // Configurar el botón de crear ingreso
      document.getElementById('create-ingreso-btn').onclick = function() {
        var patent = info.event.extendedProps.patent;
        window.location.href = '/agenda/ingresos/crear/?patent=' + encodeURIComponent(patent);
      };
    },
    dateClick: function(info) {
      console.log('Día clicado:', info.dateStr);
      calendar.changeView('timeGridDay', info.dateStr);
    }
  });
  calendar.render();
});