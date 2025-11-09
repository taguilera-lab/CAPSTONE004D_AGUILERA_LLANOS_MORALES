// incident_list.js - Funcionalidad de filtros para la lista de incidentes

document.addEventListener('DOMContentLoaded', function() {
    console.log('incident_list.js loaded');

    // Mapa para convertir valores internos de estado a texto mostrado
    const statusDisplayMap = {
        'Reportada': 'reportada',
        'Diagnostico_In_Situ': 'diagnóstico in situ',
        'OT_Generada': 'ot generada',
        'Resuelta': 'resuelta'
    };

    // Elementos del DOM
    const filterForm = document.getElementById('incident-filters');
    const container = document.getElementById('incidents-container');
    const clearFiltersBtn = document.getElementById('clear-filters');

    // Array para mantener todas las tarjetas originales
    const allCards = Array.from(container.children);

    // Función para aplicar filtros
    function applyFilters() {
        const filters = {
            patent: document.getElementById('filter-patent')?.value?.toLowerCase().trim() || '',
            incidentType: document.getElementById('filter-incident-type')?.value || '',
            severity: document.getElementById('filter-severity')?.value || '',
            category: document.getElementById('filter-category')?.value || '',
            status: document.getElementById('filter-status')?.value || '',
            reportedBy: document.getElementById('filter-reported-by')?.value?.toLowerCase().trim() || '',
            priority: document.getElementById('filter-priority')?.value || '',
            month: document.getElementById('filter-month')?.value || '',
            year: document.getElementById('filter-year')?.value || ''
        };

        console.log('Aplicando filtros:', filters);

        // Limpiar el contenedor
        container.innerHTML = '';

        // Filtrar y agregar solo las tarjetas visibles
        const visibleCards = allCards.filter(card => {
            const cardData = getCardData(card);
            return matchesFilters(cardData, filters);
        });

        // Agregar las tarjetas visibles al contenedor
        visibleCards.forEach(card => {
            container.appendChild(card);
        });

        updateResultsCount(visibleCards.length);
        console.log(`Mostrando ${visibleCards.length} de ${allCards.length} incidentes`);
    }

    // Función para obtener datos de una tarjeta
    function getCardData(card) {
        const patentElement = card.querySelector('h6 strong');
        const statusBadge = card.querySelector('.card-header .badge');
        const allPElements = card.querySelectorAll('p');
        let reportedBy = '', incidentType = '', severity = '', category = '', priority = '', month = '', year = '';

        allPElements.forEach(p => {
            const text = p.textContent.trim();
            if (text.startsWith('Por:')) {
                reportedBy = text.replace('Por:', '').trim().split(' ')[0].toLowerCase(); // Solo el nombre, sin el badge
            } else if (text.startsWith('Tipo:')) {
                incidentType = text.replace('Tipo:', '').trim();
            } else if (text.startsWith('Severidad:')) {
                severity = p.querySelector('.badge') ? p.querySelector('.badge').textContent.trim() : '';
            } else if (text.startsWith('Categoría:')) {
                category = text.replace('Categoría:', '').trim();
            } else if (text.startsWith('Prioridad:')) {
                priority = p.querySelector('.badge') ? p.querySelector('.badge').textContent.trim() : '';
            } else if (text.startsWith('Reportado:')) {
                // Extraer fecha del formato "Reportado: DD/MM/YYYY HH:MM"
                const dateMatch = text.match(/Reportado:\s*(\d{2})\/(\d{2})\/(\d{4})/);
                if (dateMatch) {
                    month = dateMatch[2]; // MM
                    year = dateMatch[3];  // YYYY
                }
            }
        });

        return {
            patent: patentElement ? patentElement.textContent.toLowerCase().trim() : '',
            status: statusBadge ? statusBadge.textContent.toLowerCase().trim() : '',
            reportedBy: reportedBy,
            incidentType: incidentType,
            severity: severity,
            category: category,
            priority: priority,
            month: month,
            year: year
        };
    }

    // Funciones auxiliares eliminadas ya que ahora extraemos la info directamente del DOM

    // Función para verificar si una tarjeta cumple con los filtros
    function matchesFilters(cardData, filters) {
        // Filtro por patente
        if (filters.patent && !cardData.patent.includes(filters.patent)) {
            return false;
        }

        // Filtro por tipo de incidente
        if (filters.incidentType && cardData.incidentType !== filters.incidentType) {
            return false;
        }

        // Filtro por severidad
        if (filters.severity && cardData.severity !== filters.severity) {
            return false;
        }

        // Filtro por categoría
        if (filters.category && cardData.category !== filters.category) {
            return false;
        }

        // Filtro por estado
        if (filters.status && cardData.status !== statusDisplayMap[filters.status]) {
            return false;
        }

        // Filtro por reportado por
        if (filters.reportedBy && !cardData.reportedBy.includes(filters.reportedBy)) {
            return false;
        }

        // Filtro por prioridad
        if (filters.priority && cardData.priority !== filters.priority) {
            return false;
        }

        // Filtro por mes
        if (filters.month && cardData.month !== filters.month) {
            return false;
        }

        // Filtro por año
        if (filters.year && cardData.year !== filters.year) {
            return false;
        }

        return true;
    }

    // Función para actualizar el contador de resultados
    function updateResultsCount(count) {
        const resultsCount = document.getElementById('results-count');
        if (resultsCount) {
            resultsCount.textContent = `Mostrando ${count} de ${allCards.length} incidentes`;
        }
    }

    // Función para limpiar filtros
    function clearFilters() {
        console.log('Limpiando filtros');

        // Limpiar el contenedor
        container.innerHTML = '';

        // Agregar todas las tarjetas de vuelta
        allCards.forEach(card => {
            container.appendChild(card);
        });

        // Limpiar los campos del formulario
        const filterInputs = filterForm.querySelectorAll('input, select');
        filterInputs.forEach(input => {
            input.value = '';
        });

        updateResultsCount(allCards.length);
        console.log(`Mostrando todos los ${allCards.length} incidentes`);
    }

    // Event listeners
    if (filterForm) {
        filterForm.addEventListener('input', applyFilters);
        filterForm.addEventListener('change', applyFilters);
    }

    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
    }

    // Inicializar contador
    updateResultsCount(allCards.length);

    console.log(`Sistema de filtros inicializado para ${allCards.length} incidentes`);
});

// Funcionalidad de selección múltiple para diagnósticos
document.addEventListener('DOMContentLoaded', function() {
    console.log('Multiple selection functionality loaded');

    const checkboxes = document.querySelectorAll('.incident-checkbox');
    const createMultipleBtn = document.getElementById('create-multiple-diagnostic-btn');
    const selectAllBtn = document.getElementById('select-all-btn');
    const clearSelectionBtn = document.getElementById('clear-selection-btn');
    const form = document.getElementById('multiple-diagnostic-form');

    // Función para actualizar el estado del botón de crear diagnóstico múltiple
    function updateCreateButton() {
        const checkedBoxes = document.querySelectorAll('.incident-checkbox:checked');
        if (createMultipleBtn) {
            createMultipleBtn.disabled = checkedBoxes.length === 0;
            createMultipleBtn.textContent = checkedBoxes.length === 0
                ? 'Crear Diagnóstico Múltiple'
                : `Crear Diagnóstico Múltiple (${checkedBoxes.length})`;
        }
    }

    // Event listener para checkboxes individuales
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateCreateButton);
    });

    // Event listener para seleccionar todos
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
            updateCreateButton();
        });
    }

    // Event listener para limpiar selección
    if (clearSelectionBtn) {
        clearSelectionBtn.addEventListener('click', function() {
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            updateCreateButton();
        });
    }

    // Event listener para el formulario
    if (form) {
        form.addEventListener('submit', function(e) {
            const checkedBoxes = document.querySelectorAll('.incident-checkbox:checked');
            if (checkedBoxes.length === 0) {
                e.preventDefault();
                alert('Por favor selecciona al menos un incidente para crear un diagnóstico.');
                return false;
            }

            if (!confirm(`¿Estás seguro de crear un diagnóstico para ${checkedBoxes.length} incidente(s)?`)) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Inicializar estado del botón
    updateCreateButton();
});
