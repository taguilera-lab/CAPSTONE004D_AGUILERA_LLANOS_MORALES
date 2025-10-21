// ingresos_list.js - Sistema de filtros para la lista de ingresos

document.addEventListener('DOMContentLoaded', function() {
    const filterInputs = document.querySelectorAll('.filter-input');
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    const resultsCount = document.getElementById('results-count');
    const clearFiltersBtn = document.getElementById('clear-filters');

    // Función para normalizar texto (quitar acentos, convertir a minúsculas)
    function normalizeText(text) {
        return text.toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
    }

    // Función para filtrar filas
    function filterRows() {
        const filters = {};

        // Recopilar valores de filtros
        filterInputs.forEach(input => {
            const columnIndex = parseInt(input.dataset.column);
            const value = input.value.trim();
            if (value) {
                filters[columnIndex] = normalizeText(value);
            }
        });

        let visibleCount = 0;

        // Aplicar filtros a cada fila
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let showRow = true;

            // Verificar cada filtro
            for (const [columnIndex, filterValue] of Object.entries(filters)) {
                const cell = cells[columnIndex];
                if (cell) {
                    // Para celdas con badges, buscar en el texto del badge
                    const badge = cell.querySelector('.badge');
                    const cellText = badge ? badge.textContent : cell.textContent;
                    const normalizedCellText = normalizeText(cellText);

                    if (!normalizedCellText.includes(filterValue)) {
                        showRow = false;
                        break;
                    }
                }
            }

            // Filtros específicos para fechas de entrada y salida
            if (showRow) {
                // Obtener fechas de la fila
                const entryDateCell = cells[3];
                const exitDateCell = cells[4];

                const entryDate = entryDateCell ? entryDateCell.textContent.trim() : '';
                const exitDate = exitDateCell ? exitDateCell.textContent.trim() : '';

                console.log('Fila datos:', {entryDate, exitDate});

                // Filtrar por fecha de entrada
                const filterEntryDate = document.getElementById('filter-entry').value;
                if (filterEntryDate && entryDate && entryDate !== '-' && !isDateInRange(entryDate, filterEntryDate)) {
                    console.log('Ocultando fila por filtro de entrada');
                    showRow = false;
                }

                // Filtrar por fecha de salida
                const filterExitDate = document.getElementById('filter-exit').value;
                if (filterExitDate && exitDate && exitDate !== '-' && !isDateInRange(exitDate, filterExitDate)) {
                    console.log('Ocultando fila por filtro de salida');
                    showRow = false;
                }
            }

            // Mostrar/ocultar fila
            row.style.display = showRow ? '' : 'none';
            if (showRow) {
                visibleCount++;
            }
        });

        // Actualizar contador de resultados
        updateResultsCount(visibleCount);
    }

    // Función para actualizar contador de resultados
    function updateResultsCount(count) {
        const total = rows.length;
        if (count === total) {
            resultsCount.textContent = `Mostrando todos los registros (${total})`;
        } else {
            resultsCount.textContent = `Mostrando ${count} de ${total} registros`;
        }
    }

    // Función para limpiar filtros
    function clearFilters() {
        filterInputs.forEach(input => {
            input.value = '';
        });

        // Limpiar filtros de fecha específicos
        const dateFilters = ['filter-entry', 'filter-exit'];
        dateFilters.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.value = '';
            }
        });

        filterRows();
    }

    // Event listeners
    filterInputs.forEach(input => {
        input.addEventListener('input', filterRows);
        input.addEventListener('change', filterRows);
    });

    // Event listeners específicos para filtros de fecha
    const dateFilters = ['filter-entry', 'filter-exit'];
    dateFilters.forEach(filterId => {
        const filterElement = document.getElementById(filterId);
        if (filterElement) {
            filterElement.addEventListener('change', filterRows);
            filterElement.addEventListener('input', filterRows);
        }
    });

    clearFiltersBtn.addEventListener('click', clearFilters);

    // Función para comparar fechas con inputs de tipo date
    function isDateInRange(cellDate, filterDate) {
        if (!cellDate || !filterDate) {
            console.log('isDateInRange: faltan parámetros', {cellDate, filterDate});
            return false;
        }

        try {
            console.log('isDateInRange: comparando', {cellDate, filterDate});

            // Parsear la fecha del filtro (viene en formato YYYY-MM-DD)
            const filterDateObj = new Date(filterDate + 'T00:00:00');
            console.log('filterDateObj:', filterDateObj);

            // Intentar parsear el formato de Django: "Jan. 4, 2025, 6:13 a.m."
            let cellDateObj = null;

            // Formato: "Jan. 4, 2025, 6:13 a.m." (inglés americano con AM/PM)
            const dateMatch = cellDate.match(/(\w+)\.\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2})\s+(a\.m\.|p\.m\.)/i);
            if (dateMatch) {
                const monthName = dateMatch[1].toLowerCase();
                const day = parseInt(dateMatch[2]);
                const year = parseInt(dateMatch[3]);
                let hour = parseInt(dateMatch[4]);
                const minute = parseInt(dateMatch[5]);
                const ampm = dateMatch[6].toLowerCase();

                const months = {
                    'jan': 0, 'feb': 1, 'mar': 2, 'apr': 3, 'may': 4, 'jun': 5,
                    'jul': 6, 'aug': 7, 'sep': 8, 'oct': 9, 'nov': 10, 'dec': 11
                };

                const month = months[monthName];
                if (month !== undefined) {
                    // Convertir a formato 24 horas
                    if (ampm === 'p.m.' && hour !== 12) hour += 12;
                    if (ampm === 'a.m.' && hour === 12) hour = 0;

                    cellDateObj = new Date(year, month, day, hour, minute);
                    console.log('cellDateObj parseado:', cellDateObj);
                }
            }

            if (!cellDateObj) {
                console.log('No se pudo parsear la fecha de la celda:', cellDate);
                return false;
            }

            // Comparar si las fechas son del mismo día (ignorar hora)
            const sameDay = cellDateObj.getFullYear() === filterDateObj.getFullYear() &&
                           cellDateObj.getMonth() === filterDateObj.getMonth() &&
                           cellDateObj.getDate() === filterDateObj.getDate();

            console.log('Comparación de fechas:', {
                cellDate: cellDateObj.toDateString(),
                filterDate: filterDateObj.toDateString(),
                sameDay
            });

            return sameDay;
        } catch (error) {
            console.error('Error parsing date:', cellDate, error);
            return false;
        }
    }

    // Inicializar contador
    updateResultsCount(rows.length);
});