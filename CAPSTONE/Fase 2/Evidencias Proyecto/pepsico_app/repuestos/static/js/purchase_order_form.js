// purchase_order_form.js
document.addEventListener('DOMContentLoaded', function() {
  const orderItemsContainer = document.getElementById('orderItems');
  
  // Solo inicializar gestión de items si existe el contenedor (solo para formularios de creación)
  if (!orderItemsContainer) {
    return;
  }

  let itemIndex = parseInt(orderItemsContainer.dataset.initialItemCount || 0);

  // Función para calcular subtotal
  function calculateSubtotal(row) {
    const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
    const unitPrice = parseFloat(row.querySelector('.unit-price-input').value) || 0;
    const subtotal = quantity * unitPrice;
    row.querySelector('.subtotal-display').value = subtotal.toFixed(2);
    return subtotal;
  }

  // Función para actualizar totales
  function updateTotals() {
    let totalItems = 0;
    let totalAmount = 0;

    document.querySelectorAll('.item-row').forEach(row => {
      totalItems++;
      totalAmount += calculateSubtotal(row);
    });

    document.getElementById('totalItems').textContent = totalItems;
    document.getElementById('totalAmount').textContent = totalAmount.toFixed(2);
  }

  // Función para agregar item
  function addItem() {
    // Obtener datos de repuestos desde el elemento data
    const sparePartsDataElement = document.getElementById('sparePartsData');
    let optionsHtml = '<option value="">Seleccionar repuesto...</option>';

    if (sparePartsDataElement) {
      try {
        const sparePartsData = JSON.parse(sparePartsDataElement.textContent);
        sparePartsData.forEach(stock => {
          optionsHtml += `<option value="${stock.repuesto_pk}" data-price="${stock.unit_cost}">
            ${stock.repuesto_name} (${stock.part_number || 'Sin número'})
          </option>`;
        });
      } catch (e) {
        // Si hay error con JSON, usar datos hardcodeados
        optionsHtml += '<option value="1" data-price="5000.00">Estudio (Sin número)</option>';
      }
    } else {
      // Si no hay elemento, usar datos hardcodeados
      optionsHtml += '<option value="1" data-price="5000.00">Estudio (Sin número)</option>';
    }

    let html = `
      <div class="item-row card mb-2">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-md-4">
              <label class="form-label">Repuesto</label>
              <select name="items[${itemIndex}][spare_part]" class="form-select spare-part-select">
                ${optionsHtml}
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Cantidad</label>
              <input type="number" name="items[${itemIndex}][quantity]" class="form-control quantity-input" min="1" value="1">
            </div>
            <div class="col-md-2">
              <label class="form-label">Precio Unit.</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" name="items[${itemIndex}][unit_price]" class="form-control unit-price-input" step="0.01" min="0" value="0.00">
              </div>
            </div>
            <div class="col-md-2">
              <label class="form-label">Subtotal</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="text" class="form-control subtotal-display" value="0.00" readonly>
              </div>
            </div>
            <div class="col-md-2">
              <button type="button" class="btn btn-outline-danger remove-item-btn mt-4">
                <i class="fas fa-trash"></i> Eliminar
              </button>
            </div>
          </div>
        </div>
      </div>
    `;

    itemIndex++;

    document.getElementById('orderItems').insertAdjacentHTML('beforeend', html);

    // Agregar event listeners al nuevo item
    const newRow = document.getElementById('orderItems').lastElementChild;
    attachItemEvents(newRow);
    updateTotals();
  }

  // Función para remover item
  function removeItem(button) {
    if (document.querySelectorAll('.item-row').length > 1) {
      button.closest('.item-row').remove();
      updateTotals();
    } else {
      alert('Debe mantener al menos un item en la orden.');
    }
  }

  // Función para manejar cambio de repuesto
  function handleSparePartChange(select) {
    const selectedOption = select.options[select.selectedIndex];
    const price = selectedOption.getAttribute('data-price') || 0;
    const row = select.closest('.item-row');
    row.querySelector('.unit-price-input').value = parseFloat(price).toFixed(2);
    calculateSubtotal(row);
    updateTotals();
  }

  // Función para adjuntar eventos a un item
  function attachItemEvents(row) {
    const sparePartSelect = row.querySelector('.spare-part-select');
    if (sparePartSelect) {
      sparePartSelect.addEventListener('change', function() {
        handleSparePartChange(this);
      });
    }

    const quantityInput = row.querySelector('.quantity-input');
    if (quantityInput) {
      quantityInput.addEventListener('input', updateTotals);
    }

    const unitPriceInput = row.querySelector('.unit-price-input');
    if (unitPriceInput) {
      unitPriceInput.addEventListener('input', updateTotals);
    }

    const removeBtn = row.querySelector('.remove-item-btn');
    if (removeBtn) {
      removeBtn.addEventListener('click', function() {
        removeItem(this);
      });
    }
  }

  // Event listeners principales
  const addButton = document.getElementById('addItemBtn');
  if (addButton) {
    addButton.addEventListener('click', function() {
      addItem();
    });
  }

  // Adjuntar eventos a items existentes
  document.querySelectorAll('.item-row').forEach(attachItemEvents);

  // Si no hay items, agregar uno por defecto
  if (document.querySelectorAll('.item-row').length === 0) {
    addItem();
  }

  // Función para guardar como borrador
  window.saveAsDraft = function() {
    const statusSelect = document.querySelector('[name="status"]');
    if (statusSelect) {
      statusSelect.value = 'DRAFT';
    }
    document.getElementById('purchaseOrderForm').submit();
  };

  // Función para reindexar items antes de enviar el formulario
  function reindexItems() {
    const itemRows = document.querySelectorAll('.item-row');
    itemRows.forEach((row, index) => {
      // Actualizar nombres de los inputs
      const sparePartSelect = row.querySelector('.spare-part-select');
      if (sparePartSelect) {
        sparePartSelect.name = `items[${index}][spare_part]`;
      }

      const quantityInput = row.querySelector('.quantity-input');
      if (quantityInput) {
        quantityInput.name = `items[${index}][quantity]`;
      }

      const unitPriceInput = row.querySelector('.unit-price-input');
      if (unitPriceInput) {
        unitPriceInput.name = `items[${index}][unit_price]`;
      }
    });
  }

  // Agregar event listener para el envío del formulario
  const purchaseForm = document.getElementById('purchaseOrderForm');
  if (purchaseForm) {
    purchaseForm.addEventListener('submit', function(e) {
      // Reindexar items antes de enviar
      reindexItems();
    });
  }

  // Inicializar cálculos
  updateTotals();
});