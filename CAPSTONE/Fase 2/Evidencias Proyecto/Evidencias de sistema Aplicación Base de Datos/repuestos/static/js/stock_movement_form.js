document.addEventListener('DOMContentLoaded', function() {
  const sparePartSelect = document.getElementById('id_repuesto');
  const quantityInput = document.getElementById('id_quantity');
  const movementTypeInputs = document.querySelectorAll('input[name="movement_type"]');

  // Función para mostrar/ocultar campos según el tipo de movimiento
  function toggleFieldsByMovementType() {
    const movementType = document.querySelector('input[name="movement_type"]:checked');
    console.log('toggleFieldsByMovementType called, checked input:', movementType);

    if (movementType) {
      const movementValue = movementType.value;
      console.log('Movement type value:', movementValue);

      const purchaseOrderField = document.getElementById('purchaseOrderField');
      console.log('purchaseOrderField element:', purchaseOrderField);

      if (movementValue === 'IN') {
        console.log('Showing purchase order field');
        purchaseOrderField.style.display = 'block';
      } else {
        console.log('Hiding purchase order field');
        purchaseOrderField.style.display = 'none';
        // Limpiar el campo cuando no es entrada
        document.getElementById('id_purchase_order').value = '';
      }
    } else {
      console.log('No movement type selected');
    }
  }

  console.log('Stock movement form JavaScript loaded');

  if (!sparePartSelect) {
    console.error('sparePartSelect (id_repuesto) not found!');
    return;
  }

  if (!quantityInput) {
    console.error('quantityInput (id_quantity) not found!');
    return;
  }

  console.log('All elements found, initializing...');

  // Función para actualizar información del stock
  function updateStockInfo() {
    const sparePartId = sparePartSelect.value;
    console.log('updateStockInfo called with sparePartId:', sparePartId);

    if (sparePartId && sparePartId !== '') {
      console.log('Making AJAX call...');
      // Hacer llamada AJAX para obtener la información del stock
      fetch(`/repuestos/api/repuesto/${sparePartId}/stock/`, {
        credentials: 'same-origin'
      })
        .then(response => {
          console.log('Response received, status:', response.status);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('Data received:', data);
          // Actualizar los valores en la interfaz
          document.getElementById('currentStock').textContent = data.current_stock || '0';
          document.getElementById('minStock').textContent = data.minimum_stock || '0';
          document.getElementById('availableStock').textContent = data.current_stock || '0';

          document.getElementById('currentStockInfo').style.display = 'block';
          console.log('Stock info updated successfully');
          updateMovementPreview();
        })
        .catch(error => {
          console.error('Error al obtener información del stock:', error);
          // Mostrar valores por defecto en caso de error
          document.getElementById('currentStock').textContent = 'Error';
          document.getElementById('minStock').textContent = 'Error';
          document.getElementById('availableStock').textContent = 'Error';
          document.getElementById('currentStockInfo').style.display = 'block';
        });
    } else {
      console.log('No sparePartId selected, hiding stock info');
      // Ocultar información cuando no hay repuesto seleccionado
      document.getElementById('currentStockInfo').style.display = 'none';
      document.getElementById('movementPreview').style.display = 'none';
    }
  }

  // Función para actualizar el preview del movimiento
  function updateMovementPreview() {
    const quantity = parseInt(quantityInput.value) || 0;
    const currentStock = parseInt(document.getElementById('currentStock').textContent) || 0;
    const movementType = document.querySelector('input[name="movement_type"]:checked').value;

    if (quantity > 0) {
      let newStock;
      if (movementType === 'IN') {
        newStock = currentStock + quantity;
      } else {
        newStock = currentStock - quantity;
      }

      document.getElementById('newStock').textContent = newStock;
      document.getElementById('movementPreview').style.display = 'block';

      // Actualizar estado
      const statusElement = document.getElementById('stockStatus');
      if (newStock <= 0) {
        statusElement.innerHTML = '<span class="badge bg-danger">Sin Stock</span>';
      } else if (newStock < 10) { // Ejemplo de stock mínimo
        statusElement.innerHTML = '<span class="badge bg-warning">Stock Bajo</span>';
      } else {
        statusElement.innerHTML = '<span class="badge bg-success">Stock Normal</span>';
      }
    } else {
      document.getElementById('movementPreview').style.display = 'none';
    }
  }

  // Event listeners
  sparePartSelect.addEventListener('change', updateStockInfo);
  quantityInput.addEventListener('input', updateMovementPreview);
  movementTypeInputs.forEach(input => {
    input.addEventListener('change', function() {
      updateMovementPreview();
      toggleFieldsByMovementType();
    });
  });

  // Inicializar
  updateStockInfo();
  toggleFieldsByMovementType();
  console.log('Stock movement form initialization complete');
});