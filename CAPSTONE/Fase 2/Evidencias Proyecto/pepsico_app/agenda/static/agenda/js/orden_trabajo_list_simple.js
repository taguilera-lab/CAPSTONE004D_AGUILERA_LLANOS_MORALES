// Órdenes de Trabajo - Lista
document.addEventListener('DOMContentLoaded', function() {
    console.log('JavaScript de órdenes de trabajo cargado');

    // Elementos básicos
    const clearFiltersBtn = document.getElementById('clear-filters');
    const resultsCount = document.getElementById('results-count');

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
        const partsIssuedFilter = document.getElementById('filter-parts-issued')?.value || '';

        console.log('Filtros activos:', { fechaFilter, mesAnioFilter });

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

            // Filtro de fecha de creación de OT
            if (fechaFilter && show) {
                const paragraphs = card.querySelectorAll('.card-body p');
                let creadaText = '';
                for (let i = 0; i < paragraphs.length; i++) {
                    const text = paragraphs[i].textContent.trim();
                    if (text.includes('Creada:')) {
                        creadaText = text.replace(/Creada\s*:/, '').trim();
                        break;
                    }
                }

                if (creadaText) {
                    const datePart = creadaText.split(' ')[0];
                    const dateParts = datePart.split('/');
                    if (dateParts.length === 3) {
                        const formattedDate = `${dateParts[2]}-${dateParts[1].padStart(2, '0')}-${dateParts[0].padStart(2, '0')}`;
                        show = (formattedDate === fechaFilter);
                        console.log('Comparando fecha de creación:', formattedDate, 'vs', fechaFilter, 'resultado:', show);
                    } else {
                        show = false;
                    }
                } else {
                    show = false;
                }
            }

            // Filtro de mes y año de creación de OT
            if (mesAnioFilter && show) {
                const paragraphs = card.querySelectorAll('.card-body p');
                let creadaText = '';
                for (let i = 0; i < paragraphs.length; i++) {
                    const text = paragraphs[i].textContent.trim();
                    if (text.includes('Creada:')) {
                        creadaText = text.replace(/Creada\s*:/, '').trim();
                        break;
                    }
                }

                if (creadaText) {
                    const datePart = creadaText.split(' ')[0];
                    const dateParts = datePart.split('/');
                    if (dateParts.length === 3) {
                        const year = dateParts[2];
                        const month = dateParts[1].padStart(2, '0');
                        const cardMonthYear = `${year}-${month}`;
                        show = (cardMonthYear === mesAnioFilter);
                        console.log('Comparando mes/año de creación:', cardMonthYear, 'vs', mesAnioFilter, 'resultado:', show);
                    } else {
                        show = false;
                    }
                } else {
                    show = false;
                }
            }

            // Filtro de repuestos emitidos
            if (partsIssuedFilter && show) {
                const paragraphs = card.querySelectorAll('.card-body p');
                let partsIssuedText = '';
                for (let i = 0; i < paragraphs.length; i++) {
                    const text = paragraphs[i].textContent.trim();
                    if (text.includes('Repuestos Emitidos:')) {
                        // Extraer el texto del badge (ahora incluye íconos)
                        const badge = paragraphs[i].querySelector('.badge');
                        if (badge) {
                            // Obtener solo el texto visible, ignorando los íconos
                            const badgeText = badge.textContent.trim();
                            // Extraer solo "Sí" o "No" del texto
                            if (badgeText.includes('Sí')) {
                                partsIssuedText = 'sí';
                            } else if (badgeText.includes('No')) {
                                partsIssuedText = 'no';
                            }
                        }
                        break;
                    }
                }
                
                if (partsIssuedFilter === 'true') {
                    show = (partsIssuedText === 'sí');
                } else if (partsIssuedFilter === 'false') {
                    show = (partsIssuedText === 'no');
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
        if (resultsCount) {
            resultsCount.textContent = 'Mostrando ' + visibleCount + ' de ' + columns.length + ' órdenes';
        }
    }

    // Función para limpiar filtros
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            const allInputs = document.querySelectorAll('input[type="text"], input[type="date"], input[type="month"], select');
            allInputs.forEach(function(input) {
                input.value = '';
            });
            applyAllFilters();
        });
    }

    // Configurar filtros de texto
    const textInputs = document.querySelectorAll('input[type="text"].filter-input');
    textInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            setTimeout(() => applyAllFilters(), 300);
        });
    });

    // Configurar filtro select
    const selectInputs = document.querySelectorAll('select.filter-input');
    selectInputs.forEach(function(select) {
        select.addEventListener('change', function() {
            applyAllFilters();
        });
    });

    // Configurar filtros de fecha
    const dateInputs = document.querySelectorAll('input[type="date"], input[type="month"]');
    dateInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            console.log('Filtro de fecha cambió:', this.id, this.value);
            applyAllFilters();
        });
    });

    // Inicializar contador
    const allCards = document.querySelectorAll('.work-order-card');
    if (resultsCount) {
        resultsCount.textContent = 'Mostrando ' + allCards.length + ' órdenes';
    }

    console.log('Filtros inicializados');
});