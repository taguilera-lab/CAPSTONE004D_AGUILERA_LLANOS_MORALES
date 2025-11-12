// Función para seleccionar/deseleccionar todos los checkboxes de una tabla
function toggleAllCheckboxes(tableId, masterCheckbox) {
  const checkboxes = document.querySelectorAll(`#${tableId} tbody input[type="checkbox"]`);
  checkboxes.forEach(checkbox => {
    checkbox.checked = masterCheckbox.checked;
  });
  updateDeleteButton(tableId);
}

// Función para actualizar el estado del botón de eliminar
function updateDeleteButton(tableId) {
  const checkboxes = document.querySelectorAll(`#${tableId} tbody input[type="checkbox"]:checked`);
  let buttonId;
  if (tableId === 'mechanics-table') {
    buttonId = 'delete-mechanics-btn';
  } else if (tableId === 'spare-parts-table') {
    buttonId = 'delete-spare_parts-btn';
  }
  const deleteBtn = document.getElementById(buttonId);
  if (deleteBtn) {
    deleteBtn.style.display = checkboxes.length > 0 ? 'inline-block' : 'none';
  }
}

// Función para mostrar el modal de confirmación
function showDeleteConfirm(tableId) {
  const checkboxes = document.querySelectorAll(`#${tableId} tbody input[type="checkbox"]:checked`);
  if (checkboxes.length === 0) return;

  const itemType = tableId === 'mechanics-table' ? 'mecánico' : 'pieza de repuesto';
  const itemTypePlural = tableId === 'mechanics-table' ? 'mecánicos' : 'piezas de repuesto';

  let message = `¿Estás seguro de que deseas eliminar `;
  if (checkboxes.length === 1) {
    message += `este ${itemType}?`;
  } else {
    message += `estos ${checkboxes.length} ${itemTypePlural}?`;
  }

  document.getElementById('deleteConfirmMessage').textContent = message;
  document.getElementById('confirmDeleteBtn').onclick = () => deleteSelectedItems(tableId);

  const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
  modal.show();
}

// Función para obtener el token CSRF de las cookies
function getCSRFToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Función para eliminar los elementos seleccionados
function deleteSelectedItems(tableId) {
  const checkboxes = document.querySelectorAll(`#${tableId} tbody input[type="checkbox"]:checked`);
  const selectedIds = Array.from(checkboxes).map(cb => cb.value);

  const itemType = tableId === 'mechanics-table' ? 'mechanics' : 'spare_parts';
  const workOrderId = document.getElementById('work-order-id').value;
  const url = `/ordenes-trabajo/${workOrderId}/delete-${itemType}/`;

  // Crear formulario para enviar los IDs
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = url;

  // Agregar token CSRF
  const csrfToken = getCSRFToken();
  if (csrfToken) {
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
  }

  // Agregar IDs seleccionados
  selectedIds.forEach(id => {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'selected_ids';
    input.value = id;
    form.appendChild(input);
  });

  document.body.appendChild(form);
  form.submit();
}

// Función para calcular horas transcurridas dentro del horario laboral (7:30 AM - 4:30 PM)
function calculateWorkingHoursElapsed(startDatetime, endDatetime) {
    // TEMPORAL: Cálculo de tiempo total sin restricciones de horario laboral (24 horas)
    // Código original comentado:
    /*
    const workStart = new Date(endDatetime);
    workStart.setHours(7, 30, 0, 0);
    const workEnd = new Date(endDatetime);
    workEnd.setHours(16, 30, 0, 0);

    let totalHours = 0;

    // Si está dentro del mismo día
    if (startDatetime.toDateString() === endDatetime.toDateString()) {
        const effectiveStart = new Date(Math.max(startDatetime, workStart));
        const effectiveEnd = new Date(Math.min(endDatetime, workEnd));

        if (effectiveStart < effectiveEnd) {
            totalHours = (effectiveEnd - effectiveStart) / 3600000; // convertir a horas
        }
    } else {
        // Trabajo que cruza días
        let currentDate = new Date(startDatetime);
        currentDate.setHours(0, 0, 0, 0);

        // Día de inicio
        if (startDatetime < workEnd) {
            const effectiveStart = new Date(Math.max(startDatetime, workStart));
            const effectiveEnd = workEnd;
            if (effectiveStart < effectiveEnd) {
                totalHours += (effectiveEnd - effectiveStart) / 3600000;
            }
        }

        // Días completos entre inicio y fin
        currentDate.setDate(currentDate.getDate() + 1);
        while (currentDate < endDatetime) {
            // Día completo de trabajo
            const dayStart = new Date(currentDate);
            dayStart.setHours(7, 30, 0, 0);
            const dayEnd = new Date(currentDate);
            dayEnd.setHours(16, 30, 0, 0);
            totalHours += (dayEnd - dayStart) / 3600000;
            currentDate.setDate(currentDate.getDate() + 1);
        }

        // Día de fin
        if (endDatetime > workStart) {
            const effectiveStart = workStart;
            const effectiveEnd = new Date(Math.min(endDatetime, workEnd));
            if (effectiveStart < effectiveEnd) {
                totalHours += (effectiveEnd - effectiveStart) / 3600000;
            }
        }
    }

    return totalHours;
    */

    // Cálculo temporal: tiempo total en horas (24/7)
    return (endDatetime - startDatetime) / 3600000; // convertir milisegundos a horas
}

// Función para actualizar los tiempos de trabajo en tiempo real
function updateWorkTimes() {
    // Verificar si las variables globales existen
    if (typeof workStartedAt === 'undefined' || typeof pausesData === 'undefined' || typeof mechanicAssignments === 'undefined') {
        return;
    }
    
    const now = new Date();
    let totalReal = 0;

    // Obtener el ID de la orden de trabajo para el almacenamiento persistente
    const workOrderId = document.getElementById('work-order-id')?.value;

    // Verificar si hay pausa global activa
    const globalPauses = pausesData['global'] || [];
    const globalActivePause = globalPauses.find(p => !p.end);

    mechanicAssignments.forEach(assignment => {
        const assignmentId = assignment.id;
        const assignedAt = assignment.assignedAt;
        const taskStartTime = assignment.taskStartTime;
        const hasTasks = assignment.hasTasks;
        
        // Solo calcular tiempo si el mecánico tiene tareas asignadas
        if (hasTasks) {
            // Para mecánicos con tareas, usar un tiempo de inicio persistente en sessionStorage
            const storageKey = `taskStartTime_${workOrderId}_${assignmentId}`;
            let storedTime = sessionStorage.getItem(storageKey);
            if (!storedTime) {
                storedTime = new Date().toISOString();
                sessionStorage.setItem(storageKey, storedTime);
            }
            const mechanicStartTime = new Date(storedTime);
            
            // Obtener todas las pausas relevantes para este mecánico:
            // - Pausas individuales del mecánico
            // - Pausas globales (que afectan a todos los mecánicos)
            const mechanicPauses = (pausesData[assignmentId.toString()] || []);
            const globalPauses = (pausesData['global'] || []);
            
            // Combinar todas las pausas relevantes y ordenarlas
            const allPauses = [...mechanicPauses, ...globalPauses].sort((a, b) => new Date(a.start) - new Date(b.start));
            
            // Verificar si hay una pausa activa (sin end)
            const activePause = allPauses.find(p => !p.end);
            
            // Calcular intervalos de trabajo
            let realTime = 0;
            let previousEnd = new Date(mechanicStartTime);
            
            for (const pause of allPauses) {
                if (pause.end) {  // Pausa completada
                    const pauseStart = new Date(pause.start);
                    const pauseEnd = new Date(pause.end);
                    // Intervalo desde previousEnd hasta pauseStart
                    if (previousEnd < pauseStart) {
                        realTime += calculateWorkingHoursElapsed(previousEnd, pauseStart);
                    }
                    // Actualizar previousEnd al pauseEnd
                    previousEnd = pauseEnd;
                } else {  // Pausa activa
                    const pauseStart = new Date(pause.start);
                    // Intervalo desde previousEnd hasta pauseStart
                    if (previousEnd < pauseStart) {
                        realTime += calculateWorkingHoursElapsed(previousEnd, pauseStart);
                    }
                    // No continuar después de pausa activa
                    break;
                }
            }
            
            // Si no hay pausa activa, agregar intervalo desde previousEnd hasta now
            if (!activePause) {
                realTime += calculateWorkingHoursElapsed(previousEnd, now);
            }
            
            const element = document.getElementById('real-time-' + assignmentId);
            if (element) {
                element.textContent = realTime.toFixed(2) + ' h';
            }
            totalReal += realTime;
        } else {
            // Si no tiene tareas asignadas, mostrar 0 horas
            const element = document.getElementById('real-time-' + assignmentId);
            if (element) {
                element.textContent = '0.00 h';
            }
        }
    });

    const totalElement = document.getElementById('total-real-time');
    if (totalElement) {
        totalElement.textContent = totalReal.toFixed(2) + ' h (real)';
    }
}

// Inicializar eventos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  initializeEventListeners();
});

// También intentar inicializar inmediatamente por si el DOM ya está listo
if (document.readyState !== 'loading') {
  initializeEventListeners();
} else {
  document.addEventListener('DOMContentLoaded', initializeEventListeners);
}

function initializeEventListeners() {
  // Agregar eventos a los checkboxes maestros
  document.querySelectorAll('input[type="checkbox"][data-toggle-all]').forEach(masterCheckbox => {
    masterCheckbox.addEventListener('change', function() {
      const tableId = this.getAttribute('data-toggle-all');
      toggleAllCheckboxes(tableId, this);
    });
  });

  // Agregar eventos a los checkboxes individuales
  document.querySelectorAll('tbody input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
      const table = this.closest('table');
      const tableId = table.id;
      updateDeleteButton(tableId);

      // Actualizar checkbox maestro si es necesario
      const masterCheckbox = document.querySelector(`input[data-toggle-all="${tableId}"]`);
      if (masterCheckbox) {
        const allCheckboxes = table.querySelectorAll('tbody input[type="checkbox"]');
        const checkedCheckboxes = table.querySelectorAll('tbody input[type="checkbox"]:checked');
        masterCheckbox.checked = allCheckboxes.length === checkedCheckboxes.length && allCheckboxes.length > 0;
        masterCheckbox.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < allCheckboxes.length;
      }
    });
  });

  // Actualizar tiempos cada segundo si las variables existen
  if (typeof workStartedAt !== 'undefined' && typeof pausesData !== 'undefined' && typeof mechanicAssignments !== 'undefined') {
    setInterval(updateWorkTimes, 1000);
    updateWorkTimes(); // Ejecutar inmediatamente
  }
}