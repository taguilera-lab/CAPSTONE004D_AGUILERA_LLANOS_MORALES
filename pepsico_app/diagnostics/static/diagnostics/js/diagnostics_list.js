// diagnostics_list.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Diagnostics list JavaScript loaded');

    // Inicializar tooltips de Bootstrap si están disponibles
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Event listeners para filtros - enviar formulario automáticamente
    const statusSelect = document.getElementById('status');
    const severitySelect = document.getElementById('severity');
    const patentInput = document.getElementById('patent');

    console.log('Filter elements found:', { statusSelect, severitySelect, patentInput });

    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            console.log('Status changed to:', this.value);
            const form = document.querySelector('form[method="get"]');
            if (form) {
                console.log('Submitting form for status change');
                form.submit();
            }
        });
    }

    if (severitySelect) {
        severitySelect.addEventListener('change', function() {
            console.log('Severity changed to:', this.value);
            const form = document.querySelector('form[method="get"]');
            if (form) {
                console.log('Submitting form for severity change');
                form.submit();
            }
        });
    }

    if (patentInput) {
        console.log('Setting up patent input listeners');
        // Para el input de patente, enviar solo cuando se presione Enter o se pierda el foco
        patentInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                console.log('Enter pressed in patent input, value:', this.value);
                const form = document.querySelector('form[method="get"]');
                if (form) {
                    form.submit();
                }
            }
        });

        patentInput.addEventListener('blur', function() {
            console.log('Patent input lost focus, value:', this.value);
            // Enviar cuando se pierde el foco (click fuera del input)
            const form = document.querySelector('form[method="get"]');
            if (form) {
                form.submit();
            }
        });
    }

    // Función para manejar clics en tarjetas de diagnóstico
    const diagnosticCards = document.querySelectorAll('.diagnostic-card');
    diagnosticCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Si el clic no fue en un botón o enlace, redirigir a la vista de detalle
            if (!e.target.closest('a, button')) {
                const detailLink = card.querySelector('a[href*="diagnostics_detail"]');
                if (detailLink) {
                    window.location.href = detailLink.href;
                }
            }
        });
    });

    // Función para actualizar el contador de diagnósticos visibles
    function updateDiagnosticsCount() {
        const visibleCards = document.querySelectorAll('.diagnostic-card[style*="display: block"], .diagnostic-card:not([style*="display"])');
        const totalCards = document.querySelectorAll('.diagnostic-card').length;

        // Actualizar el título si hay un contador
        const titleElement = document.querySelector('h1');
        if (titleElement && totalCards > 0) {
            const baseTitle = titleElement.innerHTML.split(' (')[0];
            if (visibleCards.length !== totalCards) {
                titleElement.innerHTML = `${baseTitle} (${visibleCards.length} de ${totalCards})`;
            } else {
                titleElement.innerHTML = baseTitle;
            }
        }
    }

    // Llamar a updateDiagnosticsCount cuando cambien los filtros
    if (statusSelect || severitySelect) {
        [statusSelect, severitySelect].forEach(select => {
            if (select) {
                select.addEventListener('change', updateDiagnosticsCount);
            }
        });
        updateDiagnosticsCount(); // Llamar inicialmente
    }

    // Función para manejar errores de carga de imágenes
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
        });
    });

    // Función para formatear fechas si es necesario
    function formatDates() {
        const dateElements = document.querySelectorAll('.text-muted');
        dateElements.forEach(element => {
            if (element.textContent.includes('Creado:')) {
                // Las fechas ya están formateadas en el template
                return;
            }
        });
    }

    formatDates();

    // Función para resaltar diagnósticos críticos
    function highlightCriticalDiagnostics() {
        const criticalBadges = document.querySelectorAll('.badge.bg-danger');
        criticalBadges.forEach(badge => {
            if (badge.textContent.toLowerCase().includes('crítica')) {
                const card = badge.closest('.diagnostic-card');
                if (card) {
                    card.style.borderLeft = '4px solid #dc3545';
                }
            }
        });
    }

    highlightCriticalDiagnostics();

    // Función para manejar la paginación AJAX si se implementa en el futuro
    function loadPage(pageUrl) {
        fetch(pageUrl)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const newDoc = parser.parseFromString(html, 'text/html');
                const newGrid = newDoc.querySelector('.diagnostics-grid');

                if (newGrid) {
                    document.querySelector('.diagnostics-grid').innerHTML = newGrid.innerHTML;

                    // Reinicializar eventos después de cargar nueva página
                    initializeCardEvents();
                    highlightCriticalDiagnostics();
                    updateDiagnosticsCount();
                }
            })
            .catch(error => {
                console.error('Error loading page:', error);
                // Fallback: recargar la página normalmente
                window.location.href = pageUrl;
            });
    }

    // Función para inicializar eventos de tarjetas
    function initializeCardEvents() {
        const cards = document.querySelectorAll('.diagnostic-card');
        cards.forEach(card => {
            card.addEventListener('click', function(e) {
                if (!e.target.closest('a, button')) {
                    const detailLink = card.querySelector('a[href*="diagnostics_detail"]');
                    if (detailLink) {
                        window.location.href = detailLink.href;
                    }
                }
            });
        });
    }

    // Inicializar eventos de tarjetas al cargar
    initializeCardEvents();

    // Función para mostrar/ocultar filtros en móviles
    function toggleFilters() {
        const filterCard = document.querySelector('.card.mb-4');
        if (filterCard) {
            const isVisible = filterCard.style.display !== 'none';
            filterCard.style.display = isVisible ? 'none' : 'block';
        }
    }

    // Agregar botón para toggle de filtros en móviles si es necesario
    if (window.innerWidth < 768) {
        const header = document.querySelector('.d-flex.justify-content-between');
        if (header) {
            const toggleButton = document.createElement('button');
            toggleButton.className = 'btn btn-outline-secondary d-md-none mb-2';
            toggleButton.innerHTML = '<i class="fas fa-filter"></i> Filtros';
            toggleButton.addEventListener('click', toggleFilters);

            header.insertAdjacentElement('afterend', toggleButton);
        }
    }
});