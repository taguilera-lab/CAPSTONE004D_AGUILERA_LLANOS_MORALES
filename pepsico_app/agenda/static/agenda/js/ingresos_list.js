// ingresos_list.js - Sistema de filtros para la lista de ingresos en tarjetas

document.addEventListener('DOMContentLoaded', function() {
    const filterInputs = document.querySelectorAll('.filter-input');
    const ingresosContainer = document.getElementById('ingresos-container');
    const ingresoCards = ingresosContainer.querySelectorAll('.ingreso-card');
    const resultsCount = document.getElementById('results-count');
    const clearFiltersBtn = document.getElementById('clear-filters');

    // Función para normalizar texto (quitar acentos, convertir a minúsculas)
    function normalizeText(text) {
        return text.toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
    }

    // Función para filtrar tarjetas
    function filterCards() {
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

        // Aplicar filtros a cada tarjeta
        ingresoCards.forEach(card => {
            let showCard = true;

            // Verificar cada filtro
            for (const [columnIndex, filterValue] of Object.entries(filters)) {
                const cardData = getCardData(card, columnIndex);
                const normalizedCardData = normalizeText(cardData);

                if (!normalizedCardData.includes(filterValue)) {
                    showCard = false;
                    break;
                }
            }

            // Filtros específicos para fechas de entrada y salida
            if (showCard) {
                const entryDate = getCardEntryDate(card);
                const exitDate = getCardExitDate(card);

                // Filtrar por fecha de entrada
                const filterEntryDate = document.getElementById('filter-entry').value;
                if (filterEntryDate && entryDate && !isDateInRange(entryDate, filterEntryDate)) {
                    showCard = false;
                }

                // Filtrar por fecha de salida
                const filterExitDate = document.getElementById('filter-exit').value;
                if (filterExitDate) {
                    // Si hay filtro de salida aplicado, solo mostrar tarjetas con fecha de salida válida que coincida
                    if (!exitDate || exitDate === 'Pendiente' || !isDateInRange(exitDate, filterExitDate)) {
                        showCard = false;
                    }
                }

                // Filtrar por mes/año
                const filterMonthYear = document.getElementById('filter-month-year').value;
                if (filterMonthYear && entryDate && !isMonthYearMatch(entryDate, filterMonthYear)) {
                    showCard = false;
                }
            }

            // Mostrar/ocultar tarjeta
            card.classList.toggle('hidden', !showCard);
            if (showCard) {
                visibleCount++;
            }
        });

        // Actualizar contador de resultados
        updateResultsCount(visibleCount);
    }

    // Función para obtener datos de la tarjeta según el índice de columna
    function getCardData(card, columnIndex) {
        switch (parseInt(columnIndex)) {
            case 1: // Patente
                return card.querySelector('.patent-badge').textContent;
            case 5: // Chofer
                return card.querySelector('.info-row:nth-child(3) .info-value').textContent;
            case 6: // Sucursal
                return card.querySelector('.info-row:nth-child(4) .info-value').textContent;
            case 7: // Agendado
                const badge = card.querySelector('.card-status .badge');
                return badge ? badge.textContent : '';
            case 8: // Autorización
                const authBadge = card.querySelector('.info-row:nth-child(5) .badge');
                return authBadge ? authBadge.textContent : '';
            case 9: // Entrada Registrada Por
                return card.querySelector('.info-row:nth-child(7) .info-value').textContent;
            case 10: // Salida Registrada Por
                return card.querySelector('.info-row:nth-child(8) .info-value').textContent;
            default:
                return '';
        }
    }

    // Función para obtener la fecha de entrada de la tarjeta
    function getCardEntryDate(card) {
        const entryRow = card.querySelector('.info-row:nth-child(1) .info-value');
        return entryRow ? entryRow.textContent.trim() : '';
    }

    // Función para obtener la fecha de salida de la tarjeta
    function getCardExitDate(card) {
        const exitRow = card.querySelector('.info-row:nth-child(2) .info-value');
        return exitRow ? exitRow.textContent.trim() : '';
    }

    // Función para actualizar contador de resultados
    function updateResultsCount(count) {
        const total = ingresoCards.length;
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
        const dateFilters = ['filter-entry', 'filter-exit', 'filter-month-year'];
        dateFilters.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.value = '';
            }
        });

        filterCards();
    }

    // Event listeners
    filterInputs.forEach(input => {
        input.addEventListener('input', filterCards);
        input.addEventListener('change', filterCards);
    });

    // Event listeners específicos para filtros de fecha
    const dateFilters = ['filter-entry', 'filter-exit', 'filter-month-year'];
    dateFilters.forEach(filterId => {
        const filterElement = document.getElementById(filterId);
        if (filterElement) {
            filterElement.addEventListener('change', filterCards);
            filterElement.addEventListener('input', filterCards);
        }
    });

    clearFiltersBtn.addEventListener('click', clearFilters);

    // Función para comparar fechas con inputs de tipo date
    function isDateInRange(cellDate, filterDate) {
        if (!cellDate || !filterDate) {
            return false;
        }

        try {
            // Parsear la fecha del filtro (viene en formato YYYY-MM-DD)
            const filterDateObj = new Date(filterDate + 'T00:00:00');

            // Intentar parsear el formato de Django: "d/m/Y H:i"
            let cellDateObj = null;

            // Formato: "d/m/Y H:i" (ejemplo: "26/10/2025 14:30")
            const dateMatch = cellDate.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{1,2}):(\d{2})/);
            if (dateMatch) {
                const day = parseInt(dateMatch[1]);
                const month = parseInt(dateMatch[2]) - 1; // Meses en JS van de 0-11
                const year = parseInt(dateMatch[3]);
                const hour = parseInt(dateMatch[4]);
                const minute = parseInt(dateMatch[5]);

                cellDateObj = new Date(year, month, day, hour, minute);
            }

            if (!cellDateObj) {
                return false;
            }

            // Comparar si las fechas son del mismo día (ignorar hora)
            const sameDay = cellDateObj.getFullYear() === filterDateObj.getFullYear() &&
                           cellDateObj.getMonth() === filterDateObj.getMonth() &&
                           cellDateObj.getDate() === filterDateObj.getDate();

            return sameDay;
        } catch (error) {
            console.error('Error parsing date:', cellDate, error);
            return false;
        }
    }

    // Función para comparar fechas con inputs de tipo month
    function isMonthYearMatch(cellDate, filterMonthYear) {
        if (!cellDate || !filterMonthYear) {
            return false;
        }

        try {
            // Parsear el filtro de mes/año (viene en formato YYYY-MM)
            const [filterYear, filterMonth] = filterMonthYear.split('-').map(Number);
            const filterMonthIndex = filterMonth - 1; // Meses en JS van de 0-11

            // Intentar parsear el formato de Django: "d/m/Y H:i"
            let cellDateObj = null;

            // Formato: "d/m/Y H:i" (ejemplo: "26/10/2025 14:30")
            const dateMatch = cellDate.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{1,2}):(\d{2})/);
            if (dateMatch) {
                const day = parseInt(dateMatch[1]);
                const month = parseInt(dateMatch[2]) - 1; // Meses en JS van de 0-11
                const year = parseInt(dateMatch[3]);

                cellDateObj = new Date(year, month, day);
            }

            if (!cellDateObj) {
                return false;
            }

            // Comparar si el año y mes coinciden
            const sameMonthYear = cellDateObj.getFullYear() === filterYear &&
                                 cellDateObj.getMonth() === filterMonthIndex;

            return sameMonthYear;
        } catch (error) {
            console.error('Error parsing date for month/year filter:', cellDate, error);
            return false;
        }
    }

    // Inicializar contador
    updateResultsCount(ingresoCards.length);
});
