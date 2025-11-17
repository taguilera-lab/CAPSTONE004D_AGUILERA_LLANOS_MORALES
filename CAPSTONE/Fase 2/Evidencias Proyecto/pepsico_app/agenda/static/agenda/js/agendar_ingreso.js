$(document).ready(function() {
    // Variables para el autocompletado de vehículos
    let searchTimeout;
    let selectedVehicleId = null;

    // Función para crear tarjeta de incidente
    function createIncidentCard(incident) {
        var emergencyClass = incident.is_emergency ? 'emergency' : '';
        var priorityClass = incident.priority && incident.priority.toLowerCase() === 'alta' ? 'high' : '';
        var priorityText = incident.priority ? incident.priority : 'Normal';

        var cardHtml = `
            <div class="incident-card ${emergencyClass}" data-incident-id="${incident.id}">
                <div class="incident-header">
                    <input type="checkbox" class="incident-checkbox" value="${incident.id}">
                    <span class="incident-title">${incident.name}</span>
                </div>
                <div class="incident-badges">
                    <span class="incident-type">${incident.incident_type}</span>
                    <span class="incident-priority ${priorityClass}">${priorityText}</span>
                </div>
                <div class="incident-description">${incident.description}</div>
                <div class="incident-meta">
                    <span class="incident-date">Reportado: ${incident.reported_at}</span>
                </div>
            </div>
        `;
        return cardHtml;
    }

    // Función para actualizar el campo oculto con los incidentes seleccionados
    function updateSelectedIncidents() {
        var selectedIds = [];
        $('.incident-checkbox:checked').each(function() {
            selectedIds.push($(this).val());
        });

        // Actualizar el campo oculto del formulario
        var $hiddenField = $('#id_related_incidents');
        $hiddenField.val(selectedIds);

        // Marcar tarjetas como seleccionadas
        $('.incident-card').removeClass('selected');
        $('.incident-checkbox:checked').closest('.incident-card').addClass('selected');
    }

    // Función para buscar vehículos con autocompletado
    function searchVehicles(query) {
        if (query.length < 2) {
            $('#vehicle-results').hide();
            return;
        }

        $.ajax({
            url: '/api/search-vehicles/',
            data: { q: query },
            success: function(data) {
                displayVehicleResults(data.vehicles);
            },
            error: function() {
                console.error('Error al buscar vehículos');
            }
        });
    }

    // Función para mostrar los resultados de búsqueda de vehículos
    function displayVehicleResults(vehicles) {
        var $results = $('#vehicle-results');
        var $list = $('#vehicle-list');

        if (vehicles.length === 0) {
            $results.hide();
            return;
        }

        var html = '';
        vehicles.forEach(function(vehicle) {
            html += `
                <div class="vehicle-item" data-vehicle-id="${vehicle.id}" data-patent="${vehicle.patent}">
                    <div class="vehicle-patent">${vehicle.patent}</div>
                    <div class="vehicle-details">${vehicle.brand} ${vehicle.model} (${vehicle.year})</div>
                </div>
            `;
        });

        $list.html(html);
        $results.show();

        // Event listeners para los items de vehículo
        $('.vehicle-item').click(function() {
            selectVehicle($(this));
        });
    }

    // Función para seleccionar un vehículo
    function selectVehicle($item) {
        var vehicleId = $item.data('vehicle-id');
        var patent = $item.data('patent');
        var brand = $item.find('.vehicle-details').text().split(' (')[0].split(' ')[0];
        var model = $item.find('.vehicle-details').text().split(' (')[0].split(' ')[1];
        var year = $item.find('.vehicle-details').text().split('(')[1].split(')')[0];

        selectedVehicleId = vehicleId;

        // Actualizar campo oculto
        $('#id_patent').val(patent);

        // Mostrar vehículo seleccionado
        $('#selected-patent').text(patent);
        $('#selected-brand').text(brand);
        $('#selected-model').text(model);
        $('#selected-year').text(year);

        $('#selected-vehicle').show();
        $('#vehicle-results').hide();
        $('#id_patent_search').val(patent);

        // Limpiar incidentes anteriores y cargar nuevos
        $('#incidents-container').html('<div class="no-incidents-message"><p>Selecciona un vehículo para ver los incidentes disponibles</p></div>');
        $('#id_related_incidents').val('');

        // Trigger para cargar incidentes
        loadIncidentsForVehicle(patent);
    }

    // Función para cargar incidentes de un vehículo
    function loadIncidentsForVehicle(patent) {
        var $container = $('#incidents-container');

        if (patent) {
            // Mostrar loading
            $container.html('<div class="loading-incidents">Cargando incidentes...</div>');

            // Hacer petición AJAX
            $.ajax({
                url: '/api/incidents-by-vehicle/',
                data: { patent: patent },
                success: function(data) {
                    if (data.incidents && data.incidents.length > 0) {
                        var cardsHtml = '';
                        data.incidents.forEach(function(incident) {
                            cardsHtml += createIncidentCard(incident);
                        });
                        $container.html(cardsHtml);

                        // Agregar event listeners a los checkboxes
                        $('.incident-checkbox').change(updateSelectedIncidents);

                        // Hacer las tarjetas clickables
                        $('.incident-card').click(function(e) {
                            // No hacer toggle si se hizo click en el checkbox
                            if ($(e.target).is('input[type="checkbox"]')) {
                                return;
                            }

                            var $checkbox = $(this).find('.incident-checkbox');
                            $checkbox.prop('checked', !$checkbox.prop('checked'));
                            updateSelectedIncidents();
                        });

                    } else {
                        $container.html('<div class="no-incidents-message"><p>No hay incidentes reportados para este vehículo</p></div>');
                    }
                },
                error: function() {
                    $container.html('<div class="no-incidents-message"><p>Error al cargar incidentes. Inténtalo de nuevo.</p></div>');
                }
            });
        }
    }

    // Event listener para el campo de búsqueda de vehículos
    $('#id_patent_search').on('input', function() {
        var query = $(this).val().trim();

        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function() {
            searchVehicles(query);
        }, 300); // Esperar 300ms después de que el usuario deje de escribir
    });

    // Ocultar resultados cuando se hace click fuera
    $(document).click(function(e) {
        if (!$(e.target).closest('.campo').length) {
            $('#vehicle-results').hide();
        }
    });

    // Event listener para cambiar vehículo seleccionado
    $('#change-vehicle').click(function() {
        selectedVehicleId = null;
        $('#id_patent').val('');
        $('#selected-vehicle').hide();
        $('#id_patent_search').val('').focus();
        $('#incidents-container').html('<div class="no-incidents-message"><p>Selecciona un vehículo para ver los incidentes disponibles</p></div>');
        $('#id_related_incidents').val('');
    });

    // Función para inicializar incidentes seleccionados (se llamará desde el HTML)
    window.initializeSelectedIncidents = function(selectedIds) {
        setTimeout(function() {
            selectedIds.forEach(function(id) {
                $('.incident-checkbox[value="' + id + '"]').prop('checked', true);
            });
            updateSelectedIncidents();
        }, 1000); // Esperar a que se carguen los incidentes
    };
});