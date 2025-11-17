// Función para implementar autocompletado en campos de texto
function setupAutocomplete(inputElement) {
  const $input = $(inputElement);
  const fieldType = $input.data('field');
  // Decodificar entidades HTML y parsear JSON
  const optionsDataAttr = $input.attr('data-options') || '[]';
  const decodedData = optionsDataAttr.replace(/&quot;/g, '"');
  const optionsData = JSON.parse(decodedData);
  let selectedValue = null;

  // Crear contenedor de sugerencias
  const $suggestionsContainer = $('<div class="autocomplete-suggestions position-absolute w-100 bg-white border rounded-bottom shadow-sm" style="display: none; max-height: 200px; overflow-y: auto; z-index: 1000;"></div>');
  $input.parent().css('position', 'relative').append($suggestionsContainer);

  // Función para obtener sugerencias
  function getSuggestions(query) {
    if (query.length < 1) {
      $suggestionsContainer.hide();
      return;
    }

    const filteredOptions = optionsData.filter(item =>
      item.text.toLowerCase().includes(query.toLowerCase())
    );

    displaySuggestions(filteredOptions, query);
  }

  // Función para mostrar sugerencias
  function displaySuggestions(items, query) {
    $suggestionsContainer.empty();

    if (items.length === 0) {
      $suggestionsContainer.append('<div class="px-3 py-2 text-muted">No se encontraron resultados</div>');
      $suggestionsContainer.show();
    } else {
      // Mostrar sugerencias
      items.forEach(function(item, index) {
        const $item = $('<div class="autocomplete-item px-3 py-2 cursor-pointer"></div>')
          .data('value', item.id)
          .data('text', item.text)
          .hover(
            function() { $(this).addClass('bg-light'); },
            function() { $(this).removeClass('bg-light'); }
          )
          .click(function() {
            selectItem(item.id, item.text);
          });

        // Resaltar el texto que coincide
        const highlightedText = query ? highlightMatch(item.text, query) : item.text;
        $item.html(highlightedText);

        $suggestionsContainer.append($item);
      });

      // Mostrar primera sugerencia como autocompletado inline
      if (items.length > 0 && query.length > 0) {
        const firstMatch = items[0];
        const remainingText = firstMatch.text.substring(query.length);
        const autocompleteText = query + '<span class="text-muted">' + remainingText + '</span>';

        // Crear elemento de autocompletado inline
        const $inlineSuggestion = $('<div class="autocomplete-inline position-absolute" style="pointer-events: none; color: #6c757d; z-index: 1; top: 50%; transform: translateY(-50%); left: 12px;"></div>');
        $inlineSuggestion.html(autocompleteText);

        $input.parent().append($inlineSuggestion);

        // Función para actualizar el autocompletado inline
        function updateInlineSuggestion() {
          const currentValue = $input.val();
          if (currentValue && firstMatch.text.toLowerCase().startsWith(currentValue.toLowerCase())) {
            const remaining = firstMatch.text.substring(currentValue.length);
            $inlineSuggestion.html('<span class="text-muted">' + remaining + '</span>');
            $inlineSuggestion.show();
          } else {
            $inlineSuggestion.hide();
          }
        }

        // Actualizar autocompletado inline en tiempo real
        $input.on('input.inline', updateInlineSuggestion);
        updateInlineSuggestion();

        // Al presionar Tab, autocompletar
        $input.on('keydown.inline', function(e) {
          if (e.key === 'Tab' && !$suggestionsContainer.is(':visible')) {
            e.preventDefault();
            selectItem(firstMatch.id, firstMatch.text);
            $inlineSuggestion.remove();
            $input.off('input.inline keydown.inline');
          }
        });
      }

      $suggestionsContainer.show();
    }
  }

// Función para resaltar coincidencias
function highlightMatch(text, query) {
  if (!query || query.length === 0) return text;

  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<strong>$1</strong>');
}  // Función para seleccionar un item
  function selectItem(value, text) {
    selectedValue = value;
    $input.val(text);
    $input.data('selected-value', value);
    $suggestionsContainer.hide();

    // Limpiar autocompletado inline
    $input.parent().find('.autocomplete-inline').remove();
    $input.off('input.inline keydown.inline');

    // Actualizar el campo hidden correspondiente
    const hiddenFieldName = fieldType + '_id';
    let $hiddenField = $('input[name="' + hiddenFieldName + '"]');
    if ($hiddenField.length === 0) {
      $hiddenField = $('<input type="hidden" name="' + hiddenFieldName + '">');
      $input.after($hiddenField);
    }
    $hiddenField.val(value);
  }

  // Eventos del input
  $input.on('input', function() {
    const query = $(this).val();
    selectedValue = null;
    $(this).data('selected-value', null);

    // Limpiar autocompletado inline anterior
    $input.parent().find('.autocomplete-inline').remove();
    $input.off('input.inline keydown.inline');

    getSuggestions(query);
  });

  $input.on('focus', function() {
    const query = $(this).val();
    if (query.length >= 1) {
      getSuggestions(query);
    } else {
      // Mostrar todas las opciones cuando el campo está vacío
      displaySuggestions(optionsData, '');
    }
  });

  $input.on('blur', function() {
    // Ocultar sugerencias después de un breve delay para permitir clicks
    setTimeout(function() {
      $suggestionsContainer.hide();
      // Limpiar autocompletado inline
      $input.parent().find('.autocomplete-inline').remove();
      $input.off('input.inline keydown.inline');
    }, 150);
  });

  $input.on('keydown', function(e) {
    const $items = $suggestionsContainer.find('.autocomplete-item');
    let $selected = $suggestionsContainer.find('.bg-primary');

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if ($selected.length === 0) {
        $items.first().addClass('bg-primary text-white').removeClass('bg-light');
      } else {
        $selected.removeClass('bg-primary text-white');
        const next = $selected.next('.autocomplete-item');
        if (next.length > 0) {
          next.addClass('bg-primary text-white').removeClass('bg-light');
        } else {
          $items.first().addClass('bg-primary text-white').removeClass('bg-light');
        }
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if ($selected.length === 0) {
        $items.last().addClass('bg-primary text-white').removeClass('bg-light');
      } else {
        $selected.removeClass('bg-primary text-white');
        const prev = $selected.prev('.autocomplete-item');
        if (prev.length > 0) {
          prev.addClass('bg-primary text-white').removeClass('bg-light');
        } else {
          $items.last().addClass('bg-primary text-white').removeClass('bg-light');
        }
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if ($selected.length > 0) {
        const value = $selected.data('value');
        const text = $selected.data('text');
        selectItem(value, text);
      }
    } else if (e.key === 'Escape') {
      $suggestionsContainer.hide();
      $input.blur();
    }
  });

  // Ocultar sugerencias al hacer click fuera
  $(document).on('click', function(e) {
    if (!$(e.target).closest('.autocomplete-suggestions').length && !$(e.target).is($input)) {
      $suggestionsContainer.hide();
    }
  });

  // Limpiar selección cuando se borra el texto
  $input.on('input', function() {
    if ($(this).val() === '') {
      selectedValue = null;
      $(this).data('selected-value', null);
      // Limpiar autocompletado inline
      $input.parent().find('.autocomplete-inline').remove();
      $input.off('input.inline keydown.inline');

      const hiddenFieldName = fieldType + '_id';
      $('input[name="' + hiddenFieldName + '"]').val('');
    }
  });
}

// Función para esperar a que jQuery esté disponible
function waitForJQuery(callback) {
  if (typeof jQuery !== 'undefined' && typeof $ !== 'undefined') {
    callback();
  } else {
    setTimeout(function() {
      waitForJQuery(callback);
    }, 50);
  }
}

// Envolver la inicialización en waitForJQuery
waitForJQuery(function() {
  $(document).ready(function() {
    // Inicializar campos de autocompletado
    $('.autocomplete-field').each(function() {
      setupAutocomplete(this);
    });

    // Atajos rápidos para motivos
    $('.quick-reason').click(function() {
      var reason = $(this).data('reason');
      $('#id_reason').val(reason);
    });

    // Mostrar campo de repuesto solo para ciertos tipos
    $('#id_pause_type').change(function() {
      var selectedType = $(this).val();
      var sparePartField = $('#spare-part-field');

      // Mostrar solo para tipos relacionados con stock
      if (selectedType && ['STOCK', 'PARTS'].includes(selectedType)) {
        sparePartField.show();
      } else {
        sparePartField.hide();
        $('#id_affected_spare_part').val('');
      }
    });

    // Cargar mecánicos cuando se selecciona una OT (solo si es necesario filtrar)
    $('#id_work_order').change(function() {
      var workOrderId = $(this).val();
      // Para pausa rápida, mantenemos todos los mecánicos disponibles
      // No necesitamos filtrar por OT específica
    });
  });
});