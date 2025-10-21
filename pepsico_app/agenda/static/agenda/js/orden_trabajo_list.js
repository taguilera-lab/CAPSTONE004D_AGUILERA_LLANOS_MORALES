// Órdenes de Trabajo - Lista
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== JAVASCRIPT ÓRDENES DE TRABAJO CARGADO ===');

    // Elementos básicos
    const clearFiltersBtn = document.getElementById('clear-filters');
    const resultsCount = document.getElementById('results-count');

    console.log('clearFiltersBtn encontrado:', !!clearFiltersBtn);
    console.log('resultsCount encontrado:', !!resultsCount);

    // Función básica para limpiar filtros
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            console.log('Botón limpiar filtros clickeado');

            // Limpiar todos los inputs
            const allInputs = document.querySelectorAll('input[type="text"], input[type="date"], select');
            allInputs.forEach(function(input) {
                input.value = '';
            });

            // Mostrar todas las tarjetas
            const cards = document.querySelectorAll('.work-order-card');
            cards.forEach(function(card) {
                card.style.display = 'block';
            });

            // Actualizar contador
            if (resultsCount) {
                resultsCount.textContent = 'Mostrando ' + cards.length + ' órdenes';
            }

            console.log('Filtros limpiados');
        });
    }

    // Función básica de filtro de texto
    function setupTextFilters() {
        const textInputs = document.querySelectorAll('input[type="text"].filter-input');

        textInputs.forEach(function(input) {
            input.addEventListener('input', function() {
                console.log('Filtro de texto ' + this.id + ' cambiado: "' + this.value + '"');

                const filterValue = this.value.toLowerCase();
                const cards = document.querySelectorAll('.work-order-card');
                const container = document.querySelector('.row'); // Contenedor de las cards

                // Crear un array para reordenar las cards
                const visibleCards = [];
                const hiddenCards = [];

                cards.forEach(function(card) {
                    let show = true;

                    if (filterValue) {
                        if (input.id === 'filter-patent') {
                            // Para filtro de patente, buscar solo en el header h6
                            const patentElement = card.querySelector('.card-header h6');
                            const patentText = patentElement ? patentElement.textContent.toLowerCase() : '';
                            // Remover el icono si existe
                            const cleanPatentText = patentText.replace('🚗', '').trim();
                            if (cleanPatentText.indexOf(filterValue) === -1) {
                                show = false;
                            }
                        } else if (input.id === 'filter-chofer') {
                            // Para filtro de chofer, buscar solo en el párrafo que contiene "Chofer:"
                            const paragraphs = card.querySelectorAll('.card-body p');
                            let choferText = '';
                            for (let i = 0; i < paragraphs.length; i++) {
                                if (paragraphs[i].textContent.includes('Chofer:')) {
                                    choferText = paragraphs[i].textContent.replace('Chofer:', '').trim().toLowerCase();
                                    break;
                                }
                            }
                            if (choferText.indexOf(filterValue) === -1) {
                                show = false;
                            }
                        } else {
                            // Para otros filtros de texto, buscar en todo el texto
                            const cardText = card.textContent.toLowerCase();
                            if (cardText.indexOf(filterValue) === -1) {
                                show = false;
                            }
                        }
                    }

                    if (show) {
                        visibleCards.push(card);
                    } else {
                        hiddenCards.push(card);
                    }
                });

                // Reorganizar las cards: primero las visibles, luego las ocultas
                const allCards = visibleCards.concat(hiddenCards);

                // Limpiar el contenedor
                while (container.firstChild) {
                    container.removeChild(container.firstChild);
                }

                // Reagregar las cards en el nuevo orden
                allCards.forEach(function(card) {
                    container.appendChild(card);
                });

                // Actualizar contador
                if (resultsCount) {
                    resultsCount.textContent = 'Mostrando ' + visibleCards.length + ' de ' + cards.length + ' órdenes';
                }
            });
        });
    }

    // Función básica de filtro select
    function setupSelectFilters() {
        const selectInputs = document.querySelectorAll('select.filter-input');

        selectInputs.forEach(function(select) {
            select.addEventListener('change', function() {
                console.log('Filtro select ' + this.id + ' cambiado: "' + this.value + '"');

                const filterValue = this.value.toLowerCase();
                const cards = document.querySelectorAll('.work-order-card');
                const container = document.querySelector('.row'); // Contenedor de las cards

                // Crear un array para reordenar las cards
                const visibleCards = [];
                const hiddenCards = [];

                cards.forEach(function(card) {
                    let show = true;

                    if (filterValue && filterValue !== '') {
                        // Buscar en el badge de estado
                        const badge = card.querySelector('.badge');
                        const badgeText = badge ? badge.textContent.toLowerCase() : '';

                        if (filterValue === 'sin orden') {
                            // Mostrar solo cards sin badge o con "Sin Orden"
                            show = (badgeText === '' || badgeText.indexOf('sin orden') !== -1);
                        } else {
                            // Mostrar cards que coincidan con el estado
                            show = (badgeText.indexOf(filterValue) !== -1);
                        }
                    }

                    if (show) {
                        visibleCards.push(card);
                    } else {
                        hiddenCards.push(card);
                    }
                });

                // Reorganizar las cards: primero las visibles, luego las ocultas
                const allCards = visibleCards.concat(hiddenCards);

                // Limpiar el contenedor
                while (container.firstChild) {
                    container.removeChild(container.firstChild);
                }

                // Reagregar las cards en el nuevo orden
                allCards.forEach(function(card) {
                    container.appendChild(card);
                });

                // Actualizar contador
                if (resultsCount) {
                    resultsCount.textContent = 'Mostrando ' + visibleCards.length + ' de ' + cards.length + ' órdenes';
                }
            });
        });
    }

    // Inicializar filtros
    setupTextFilters();
    setupSelectFilters();

    // Inicializar contador
    const allCards = document.querySelectorAll('.work-order-card');
    if (resultsCount) {
        resultsCount.textContent = 'Mostrando ' + allCards.length + ' órdenes';
    }

    console.log('=== INICIALIZACIÓN COMPLETADA ===');
    console.log('Total de tarjetas encontradas:', allCards.length);
});