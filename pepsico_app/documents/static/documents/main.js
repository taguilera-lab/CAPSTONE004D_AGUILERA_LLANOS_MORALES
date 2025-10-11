const tableFields = {
  'tabla-sites': ['Editar', 'ID', 'Nombre', 'Cantidad de Patentes'],
  'tabla-sapequipment': ['Editar', 'ID', 'Código', 'Descripción'],
  'tabla-ceco': ['Editar', 'ID', 'Código', 'Nombre', 'Tipo', 'Descripción'],
  'tabla-vehicletypes': ['Editar', 'ID', 'Nombre', 'Site', 'Datos'],
  'tabla-vehiclestatus': ['Editar', 'ID', 'Nombre', 'Descripción'],
  'tabla-vehicles': ['Editar', 'Patente', 'Equipo', 'CECO', 'Marca', 'Modelo', 'Año', 'Edad', 'Vida Útil', 'Kilometraje', 'Site', 'Operativo', 'Respaldo', 'Fuera de Servicio', 'Tipo', 'Plan', 'Siniestro', 'Observaciones', 'Cumplimiento', 'TCT', 'Geotab', 'Subasta', 'Estado'],
  'tabla-roles': ['Editar', 'ID', 'Nombre', 'Descripción', 'Es Supervisor'],
  'tabla-userstatus': ['Editar', 'ID', 'Nombre', 'Descripción'],
  'tabla-flotausers': ['Editar', 'ID', 'Nombre', 'Rol', 'Patente', 'Estado', 'Observaciones', 'GPID'],
  'tabla-routes': ['Editar', 'ID', 'Código de Ruta', 'GTM', 'Conductor', 'Patente Camión', 'Comentario'],
  'tabla-ingresos': ['Editar', 'ID', 'Patente', 'Tipo de Servicio', 'Fecha de Entrada', 'Fecha de Salida', 'Chofer', 'Supervisor', 'Observaciones', 'Autorización'],
  'tabla-servicetypes': ['Editar', 'ID', 'Nombre', 'Descripción', 'Site'],
  'tabla-tasks': ['Editar', 'ID', 'Ingreso', 'Descripción', 'Urgencia', 'Fecha de Inicio', 'Fecha de Fin', 'Tipo de Servicio', 'Supervisor'],
  'tabla-taskassignments': ['Editar', 'ID', 'Tarea', 'Usuario'],
  'tabla-pauses': ['Editar', 'ID', 'Asignación', 'Motivo', 'Duración', 'Autorización', 'Fecha de Inicio', 'Fecha de Fin'],
  'tabla-documents': ['Editar', 'ID', 'Ingreso', 'Tipo', 'Ruta del Archivo', 'Fecha de Subida', 'Usuario'],
  'tabla-repuestos': ['Editar', 'ID', 'Nombre', 'Cantidad', 'Tarea', 'Fecha de Entrega'],
  'tabla-notifications': ['Editar', 'ID', 'Destinatario', 'Mensaje', 'Fecha de Envío', 'Tipo'],
  'tabla-reports': ['Editar', 'ID', 'Tipo', 'Fecha de Generación', 'Datos', 'Usuario'],
  'tabla-maintenanceschedules': ['Editar', 'ID', 'Patente', 'Tipo de Servicio', 'Fecha de Inicio', 'Fecha de Fin', 'Regla de Recurrencia', 'Recordatorio (min)', 'Usuario Asignado', 'Supervisor', 'Estado', 'Observaciones']
};

let modoActual = 'normal'; // 'normal', 'editar', 'eliminar'

function getCookie(name) {
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

function activarModoEditar() {
  if (modoActual === 'editar') {
    modoActual = 'normal';
    document.getElementById('btnEliminarSeleccionados').style.display = 'none';
  } else {
    modoActual = 'editar';
    document.getElementById('btnEliminarSeleccionados').style.display = 'none';
  }
  actualizarVistaTabla();
}

function activarModoEliminar() {
  if (modoActual === 'eliminar') {
    modoActual = 'normal';
    document.getElementById('btnEliminarSeleccionados').style.display = 'none';
  } else {
    modoActual = 'eliminar';
    document.getElementById('btnEliminarSeleccionados').style.display = 'inline-block';
  }
  actualizarVistaTabla();
}

function actualizarVistaTabla() {
  const selectedTableId = document.getElementById('tablaSelector').value;
  const selectedTable = document.getElementById(selectedTableId);
  const thead = selectedTable.querySelector('thead tr');
  const tbody = selectedTable.querySelector('tbody');

  // Limpiar columnas dinámicas previas
  const dynamicHeaders = thead.querySelectorAll('.dynamic-header');
  dynamicHeaders.forEach(header => header.remove());

  const dynamicCells = tbody.querySelectorAll('.dynamic-cell');
  dynamicCells.forEach(cell => cell.remove());

  if (modoActual === 'editar') {
    // Mostrar columna Editar (primera columna)
    mostrarColumnaEditar(selectedTable);
  } else if (modoActual === 'eliminar') {
    // Agregar columnas Seleccionado y Eliminar
    agregarColumnasEliminar(selectedTable);
  } else {
    // Modo normal - ocultar columna Editar
    ocultarColumnaEditar(selectedTable);
  }
}

function mostrarColumnaEditar(table) {
  table.querySelectorAll('.edit-column').forEach(cell => cell.style.display = '');
}

function ocultarColumnaEditar(table) {
  table.querySelectorAll('.edit-column').forEach(cell => cell.style.display = 'none');
}

function agregarColumnasEliminar(table) {
  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');

  // Agregar encabezado Seleccionado
  const thSeleccionado = document.createElement('th');
  thSeleccionado.textContent = 'Seleccionado';
  thSeleccionado.className = 'dynamic-header';
  thead.insertBefore(thSeleccionado, thead.firstChild);

  // Agregar celdas checkbox a las filas de datos
  const rows = tbody.querySelectorAll('tr:not([colspan])');
  rows.forEach((row, index) => {
    // Checkbox
    const tdCheckbox = document.createElement('td');
    tdCheckbox.className = 'dynamic-cell';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'delete-checkbox';
    tdCheckbox.appendChild(checkbox);
    row.insertBefore(tdCheckbox, row.firstChild);
  });

  // Ocultar columna Editar original
  ocultarColumnaEditar(table);
}

function confirmarEliminacion(index) {
  if (confirm('¿Seguro deseas eliminar este registro?')) {
    // Aquí iría la lógica para eliminar el registro
    alert('Registro eliminado (simulado)');
  }
}

function construirTablaEditar(tableId, thead, tbody) {
  // Construir encabezado
  const fields = tableFields[tableId];
  fields.forEach(field => {
    const th = document.createElement('th');
    th.textContent = field;
    thead.appendChild(th);
  });

  // Construir filas de datos
  const dataRows = tbody.querySelectorAll('tr:not([colspan])');
  dataRows.forEach((row, index) => {
    // Aquí necesitaríamos acceder a los datos originales
    // Por simplicidad, recrearemos la estructura
    reconstruirFilaEditar(tableId, row, index);
  });
}

function construirTablaEliminar(tableId, thead, tbody) {
  // Encabezado con Seleccionado
  const thSeleccionado = document.createElement('th');
  thSeleccionado.textContent = 'Seleccionado';
  thead.appendChild(thSeleccionado);

  // Agregar campos de datos restantes
  const fields = tableFields[tableId].slice(1); // Sin "Editar"
  fields.forEach(field => {
    const th = document.createElement('th');
    th.textContent = field;
    thead.appendChild(th);
  });

  // Construir filas de datos
  const dataRows = tbody.querySelectorAll('tr:not([colspan])');
  dataRows.forEach((row, index) => {
    reconstruirFilaEliminar(tableId, row, index);
  });
}

function construirTablaNormal(tableId, thead, tbody) {
  // Encabezado normal sin columna Editar
  const fields = tableFields[tableId].slice(1); // Sin "Editar"
  fields.forEach(field => {
    const th = document.createElement('th');
    th.textContent = field;
    thead.appendChild(th);
  });

  // Construir filas de datos
  const dataRows = tbody.querySelectorAll('tr:not([colspan])');
  dataRows.forEach((row, index) => {
    reconstruirFilaNormal(tableId, row, index);
  });
}

function reconstruirFilaEditar(tableId, row, index) {
  // Esta función necesitaría acceder a los datos Django
  // Por ahora, es un placeholder
  row.innerHTML = '<td><button>Editar</button></td><td colspan="' + (tableFields[tableId].length - 1) + '">Datos de fila ' + (index + 1) + '</td>';
}

function reconstruirFilaEliminar(tableId, row, index) {
  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.className = 'delete-checkbox';

  row.innerHTML = '';
  const tdCheckbox = document.createElement('td');
  tdCheckbox.appendChild(checkbox);
  row.appendChild(tdCheckbox);

  // Agregar datos restantes
  for (let i = 1; i < tableFields[tableId].length; i++) {
    const td = document.createElement('td');
    td.textContent = 'Dato ' + i;
    row.appendChild(td);
  }
}

function reconstruirFilaNormal(tableId, row, index) {
  row.innerHTML = '';
  for (let i = 1; i < tableFields[tableId].length; i++) {
    const td = document.createElement('td');
    td.textContent = 'Dato ' + i;
    row.appendChild(td);
  }
}

function eliminarSeleccionados() {
  const checkboxes = document.querySelectorAll('.delete-checkbox:checked');
  if (checkboxes.length === 0) {
    alert('No hay registros seleccionados');
    return;
  }

  if (!confirm(`¿Seguro deseas eliminar ${checkboxes.length} registro(s)?`)) {
    return;
  }

  const selectedTableId = document.getElementById('tablaSelector').value;
  const modelo = selectedTableId.replace('tabla-', ''); // ej. 'sites'
  const idIndex = modoActual === 'eliminar' ? 3 : 2; // En eliminar, ID es tercera columna
  const ids = Array.from(checkboxes).map(cb => cb.closest('tr').querySelector(`td:nth-child(${idIndex})`).textContent.trim());

  const csrftoken = getCookie('csrftoken');

  const params = new URLSearchParams();
  params.append('modelo', modelo);
  ids.forEach(id => params.append('ids[]', id));

  fetch('/datos/eliminar/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken,
    },
    body: params,
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => {
    if (data.success) {
      alert(data.message);
      // Recargar la página o actualizar la tabla
      location.reload();
    } else {
      alert('Error: ' + data.message);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Error al procesar la solicitud');
  });
}

function updateFieldSelector(tableId) {
  const fieldSelector = document.getElementById('fieldSelector');
  fieldSelector.innerHTML = '<option value="all">Todos</option>';
  if (tableFields[tableId]) {
    let fields = tableFields[tableId];
    // En modo normal, excluir la columna "Editar"
    if (modoActual === 'normal') {
      fields = fields.slice(1);
    }
    // En modo eliminar, excluir la columna "Editar" también
    else if (modoActual === 'eliminar') {
      fields = fields.slice(1);
    }
    // En modo editar, incluir todos los campos

    fields.forEach(field => {
      const option = document.createElement('option');
      option.value = field;
      option.textContent = field;
      fieldSelector.appendChild(option);
    });
  }
}

function filterTable() {
  const searchTerm = document.getElementById('searchInput').value.toLowerCase();
  const selectedField = document.getElementById('fieldSelector').value;
  const selectedTableId = document.getElementById('tablaSelector').value;
  const selectedTable = document.getElementById(selectedTableId);
  const rows = selectedTable.querySelectorAll('tbody tr');

  rows.forEach(row => {
    const cells = Array.from(row.querySelectorAll('td'));
    let match = false;

    if (selectedField === 'all') {
      // En modo eliminar, excluir la primera columna (checkbox)
      const startIndex = modoActual === 'eliminar' ? 1 : 0;
      match = cells.slice(startIndex).some(cell => cell.textContent.toLowerCase().includes(searchTerm));
    } else {
      const fieldIndex = tableFields[selectedTableId].indexOf(selectedField);
      if (fieldIndex !== -1) {
        // Ajustar índice según el modo
        let adjustedIndex = fieldIndex;
        if (modoActual === 'eliminar') {
          adjustedIndex += 1; // +1 por la columna checkbox
        } else if (modoActual === 'normal') {
          adjustedIndex -= 1; // -1 porque no hay columna Editar
        }
        // En modo editar, fieldIndex ya incluye la columna Editar

        if (cells[adjustedIndex]) {
          match = cells[adjustedIndex].textContent.toLowerCase().includes(searchTerm);
        }
      }
    }

    row.style.display = match || !searchTerm ? '' : 'none';
  });
}

function mostrarTabla() {
  var selector = document.getElementById('tablaSelector');
  var valor = selector.value;
  var tablas = document.querySelectorAll('.tabla-contenedor');
  tablas.forEach(function(tabla) {
    tabla.style.display = 'none';
  });
  document.getElementById(valor).style.display = 'block';

  // Mantener el modo actual, solo ocultar el botón si no está en modo eliminar
  if (modoActual !== 'eliminar') {
    document.getElementById('btnEliminarSeleccionados').style.display = 'none';
  }

  // Reset search
  document.getElementById('searchInput').value = '';
  updateFieldSelector(valor);
  filterTable();
  actualizarVistaTabla();
}

function editarRegistro(modelo, pk) {
  window.location.href = `/datos/formulario/editar/${modelo}/${pk}/`;
}

window.onload = function() {
  mostrarTabla();
  document.getElementById('searchInput').addEventListener('input', filterTable);
  document.getElementById('fieldSelector').addEventListener('change', filterTable);
};