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
}