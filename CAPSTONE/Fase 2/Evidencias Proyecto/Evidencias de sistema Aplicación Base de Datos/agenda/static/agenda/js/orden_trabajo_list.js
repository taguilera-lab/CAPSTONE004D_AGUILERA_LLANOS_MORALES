// Órdenes de Trabajo - Lista
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== JAVASCRIPT ÓRDENES DE TRABAJO CARGADO ===');

    // Elementos básicos
    const clearFiltersBtn = document.getElementById('clear-filters');
    const resultsCount = document.getElementById('results-count');

    console.log('clearFiltersBtn encontrado:', !!clearFiltersBtn);
    console.log('resultsCount encontrado:', !!resultsCount);

    // Función para aplicar todos los filtros combinados
    function applyAllFilters() {
        console.log('Aplicando filtros...');
        const container = document.getElementById('work-orders-container');
        const columns = container ? container.querySelectorAll('.col-md-6.col-lg-4.mb-4') : [];
        
        // Obtener valores de filtros
        const patentFilter = document.getElementById('filter-patent')?.value?.toLowerCase().trim() || '';
        const choferFilter = document.getElementById('filter-chofer')?.value?.toLowerCase().trim() || '';
        const estadoFilter = document.querySelector('select.filter-input')?.value?.toLowerCase() || '';
        const fechaFilter = document.getElementById('filter-entry-date')?.value || '';
        const mesAnioFilter = document.getElementById('filter-month-year')?.value || '';

        console.log('Filtros:', { patentFilter, choferFilter, estadoFilter, fechaFilter, mesAnioFilter });

        let visibleCount = 0;
        columns.forEach(function(column) {
            const card = column.querySelector('.work-order-card');
            if (!card) {
                column.style.display = 'none';
                return;
            }

            let show = true;

            // Filtro de patente
            if (patentFilter) {
                const patentElement = card.querySelector('.card-header h6');
                const patentText = patentElement ? patentElement.textContent.toLowerCase() : '';
                if (patentText.indexOf(patentFilter) === -1) {
                    show = false;
                }
            }

            // Filtro de chofer
            if (choferFilter && show) {
                const paragraphs = card.querySelectorAll('.card-body p');
                let choferText = '';
                for (let i = 0; i < paragraphs.length; i++) {
                    if (paragraphs[i].textContent.includes('Chofer:')) {
                        choferText = paragraphs[i].textContent.replace('Chofer:', '').trim().toLowerCase();
                        break;
                    }
                }
                if (choferText.indexOf(choferFilter) === -1) {
                    show = false;
                }
            }

            // Filtro de estado
            if (estadoFilter && show) {
                const badge = card.querySelector('.badge');
                const badgeText = badge ? badge.textContent.toLowerCase() : '';
                if (estadoFilter === 'sin orden') {
                    show = (badgeText === '' || badgeText.indexOf('sin orden') !== -1);
                } else {
                    show = (badgeText.indexOf(estadoFilter) !== -1);
                }
            }

            // Filtro de fecha de entrada
            if (fechaFilter && show) {
                const paragraphs = card.querySelectorAll('.card-body p');
                let entradaText = '';
                for (let i = 0; i < paragraphs.length; i++) {
                    const text = paragraphs[i].textContent.trim();
                    if (text.includes('Entrada:')) {
                        entradaText = text.replace(/Entrada\s*:/, '').trim();
                        break;
                    }
                }

                if (entradaText) {
                    const datePart = entradaText.split(' ')[0];
                    const dateParts = datePart.split('/');
                    if (dateParts.length === 3) {
                        const formattedDate = `${dateParts[2]}-${dateParts[1].padStart(2, '0')}-${dateParts[0].padStart(2, '0')}`;
                        show = (formattedDate === fechaFilter);
                    } else {
                        show = false;
                    }
                } else {
                    show = false;
                }
            }

            // Filtro de mes y año
            if (mesAnioFilter && show) {
                const paragraphs = card.querySelectorAll('.card-body p');
                let entradaText = '';
                for (let i = 0; i < paragraphs.length; i++) {
                    const text = paragraphs[i].textContent.trim();
                    if (text.includes('Entrada:')) {
                        entradaText = text.replace(/Entrada\s*:/, '').trim();
                        break;
                    }
                }

                if (entradaText) {
                    const datePart = entradaText.split(' ')[0];
                    const dateParts = datePart.split('/');
                    if (dateParts.length === 3) {
                        const year = dateParts[2];
                        const month = dateParts[1].padStart(2, '0');
                        const cardMonthYear = `${year}-${month}`;
                        show = (cardMonthYear === mesAnioFilter);
                    } else {
                        show = false;
                    }
                } else {
                    show = false;
                }
            }

            // Aplicar visibilidad
            if (show) {
                column.style.display = '';
                visibleCount++;
            } else {
                column.style.display = 'none';
            }
        });

        // Actualizar contador
        const resultsCount = document.getElementById('results-count');
        if (resultsCount) {
            resultsCount.textContent = 'Mostrando ' + visibleCount + ' de ' + columns.length + ' órdenes';
        }

        console.log('Filtros aplicados. Visibles:', visibleCount);
    }

    // Función para restaurar el orden original
    function restoreOriginalOrder() {
        console.log('RESTAURANDO ORDEN ORIGINAL');
        // Limpiar todos los filtros
        const allInputs = document.querySelectorAll('input[type="text"], input[type="date"], input[type="month"], select');
        allInputs.forEach(function(input) {
            input.value = '';
        });
        // Aplicar filtros (que estarán vacíos, mostrando todo)
        applyAllFilters();
    }

    // Guardar el orden original (no necesitamos guardar referencias, usaremos data-id)
    console.log('Sistema de filtros inicializado');

    // Función básica para limpiar filtros
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            console.log('Botón limpiar filtros clickeado');

            // Limpiar todos los inputs
            const allInputs = document.querySelectorAll('input[type="text"], input[type="date"], input[type="month"], select');
            allInputs.forEach(function(input) {
                input.value = '';
                console.log('Input limpiado:', input.id);
            });

            // Aplicar filtros (que estarán vacíos, mostrando todo)
            applyAllFilters();
        });
    }

    // Función básica de filtro de texto
    function setupTextFilters() {
        const textInputs = document.querySelectorAll('input[type="text"].filter-input');

        textInputs.forEach(function(input) {
            let filterTimeout;
            input.addEventListener('input', function() {
                clearTimeout(filterTimeout);
                filterTimeout = setTimeout(() => {
                    console.log('Filtro de texto ' + this.id + ' cambiado: "' + this.value + '"');
                    // Aplicar todos los filtros combinados
                    applyAllFilters();
                }, 100); // Delay de 100ms para evitar llamadas excesivas
            });
        });
    }

    // Función básica de filtro select
    function setupSelectFilters() {
        const selectInputs = document.querySelectorAll('select.filter-input');

        selectInputs.forEach(function(select) {
            select.addEventListener('change', function() {
                console.log('Filtro select ' + this.id + ' cambiado: "' + this.value + '"');
                // Aplicar todos los filtros combinados
                applyAllFilters();
            });
        });
    }

    // Función básica de filtro de fecha
    function setupDateFilters() {
        const dateInputs = document.querySelectorAll('input[type="date"], input[type="month"]');

        console.log('Configurando filtros de fecha, elementos encontrados:', dateInputs.length);

        dateInputs.forEach(function(input) {
            console.log('Configurando event listener para:', input.id, input.type);
            input.addEventListener('change', function() {
                console.log('=== EVENTO CHANGE EN FILTRO DE FECHA ===');
                console.log('Filtro de fecha ' + this.id + ' cambiado: "' + this.value + '"');
                // Aplicar todos los filtros combinados
                setTimeout(() => applyAllFilters(), 100);
            });
            input.addEventListener('input', function() {
                console.log('=== EVENTO INPUT EN FILTRO DE FECHA ===');
                console.log('Filtro de fecha ' + this.id + ' input: "' + this.value + '"');
                // Aplicar todos los filtros combinados
                setTimeout(() => applyAllFilters(), 100);
            });
        });
    }

    // Inicializar filtros
    console.log('=== INICIALIZANDO FILTROS ===');
    setupTextFilters();
    setupSelectFilters();
    setupDateFilters();

    // Inicializar contador
    const allCards = document.querySelectorAll('.work-order-card');
    console.log('Total de tarjetas encontradas al inicializar:', allCards.length);
    if (resultsCount) {
        resultsCount.textContent = 'Mostrando ' + allCards.length + ' órdenes';
    }

    console.log('=== INICIALIZACIÓN COMPLETADA ===');
});