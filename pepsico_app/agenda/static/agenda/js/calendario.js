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

      // Mostrar el modal
      document.getElementById('eventModal').style.display = 'block';
      console.log('Modal abierto');
    },
    dateClick: function(info) {
      console.log('Día clicado:', info.dateStr);
      calendar.changeView('timeGridDay', info.dateStr);
    }
  });
  calendar.render();

  // Cerrar el modal
  var closeBtn = document.querySelector('#eventModal .modal-close');
  console.log('Botón close encontrado:', closeBtn);
  if (closeBtn) {
    closeBtn.addEventListener('click', function() {
      console.log('Cerrando modal con X');
      document.getElementById('eventModal').style.display = 'none';
    });
  } else {
    console.log('No se encontró el botón de cerrar');
  }

  // Cerrar el modal al hacer clic fuera
  window.addEventListener('click', function(event) {
    var modal = document.getElementById('eventModal');
    if (event.target == modal) {
      console.log('Cerrando modal con clic afuera');
      modal.style.display = 'none';
    }
  });
});