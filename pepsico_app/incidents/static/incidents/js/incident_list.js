// incident_list.js - Funcionalidad de filtros para la lista de incidentes

document.addEventListener('DOMContentLoaded', function() {
    console.log('incident_list.js loaded');

    // Elementos del DOM
    const filterForm = document.getElementById('incident-filters');
    const incidentCards = document.querySelectorAll('.incident-card');
    const clearFiltersBtn = document.getElementById('clear-filters');

    // Función para aplicar filtros
    function applyFilters() {
        const filters = {
            patent: document.getElementById('filter-patent')?.value?.toLowerCase().trim() || '',
            incidentType: document.getElementById('filter-incident-type')?.value || '',
            severity: document.getElementById('filter-severity')?.value || '',
            category: document.getElementById('filter-category')?.value || '',
            status: document.getElementById('filter-status')?.value || '',
            reportedBy: document.getElementById('filter-reported-by')?.value?.toLowerCase().trim() || '',
            priority: document.getElementById('filter-priority')?.value || ''
        };

        console.log('Aplicando filtros:', filters);

        let visibleCount = 0;

        incidentCards.forEach(card => {
            const cardData = getCardData(card);
            const isVisible = matchesFilters(cardData, filters);

            card.style.display = isVisible ? 'block' : 'none';
            if (isVisible) visibleCount++;
        });

        updateResultsCount(visibleCount);
        console.log(`Mostrando ${visibleCount} de ${incidentCards.length} incidentes`);
    }

    // Función para obtener datos de una tarjeta
    function getCardData(card) {
        const patentElement = card.querySelector('h6 strong');
        const statusBadge = card.querySelector('.badge');
        const reportedByElement = card.querySelector('p:contains("Por:")');
        const typeElement = card.querySelector('p:contains("Tipo:")');
        const severityElement = card.querySelector('p:contains("Severidad:") .badge');
        const categoryElement = card.querySelector('p:contains("Categoría:")');
        const priorityElement = card.querySelector('p:contains("Prioridad:") .badge');

        return {
            patent: patentElement ? patentElement.textContent.toLowerCase().trim() : '',
            status: statusBadge ? statusBadge.textContent.toLowerCase().trim() : '',
            reportedBy: reportedByElement ? reportedByElement.textContent.replace('Por:', '').trim().toLowerCase() : '',
            incidentType: typeElement ? typeElement.textContent.replace('Tipo:', '').trim() : '',
            severity: severityElement ? severityElement.textContent.trim() : '',
            category: categoryElement ? categoryElement.textContent.replace('Categoría:', '').trim() : '',
            priority: priorityElement ? priorityElement.textContent.trim() : ''
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
        if (filters.status && cardData.status !== filters.status.toLowerCase()) {
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

        return true;
    }

    // Función para actualizar el contador de resultados
    function updateResultsCount(count) {
        const resultsCount = document.getElementById('results-count');
        if (resultsCount) {
            resultsCount.textContent = `Mostrando ${count} de ${incidentCards.length} incidentes`;
        }
    }

    // Función para limpiar filtros
    function clearFilters() {
        const filterInputs = filterForm.querySelectorAll('input, select');
        filterInputs.forEach(input => {
            input.value = '';
        });
        applyFilters();
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
    updateResultsCount(incidentCards.length);

    console.log(`Sistema de filtros inicializado para ${incidentCards.length} incidentes`);
});
