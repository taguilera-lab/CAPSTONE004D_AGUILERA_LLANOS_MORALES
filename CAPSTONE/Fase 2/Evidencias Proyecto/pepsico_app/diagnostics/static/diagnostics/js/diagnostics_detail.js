// diagnostics_detail.js

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap si están disponibles
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Función para marcar diagnóstico como resuelto
    window.markAsResolved = function(diagnosticId) {
        if (confirm('¿Está seguro de que desea marcar este diagnóstico como resuelto?')) {
            const button = event.target.closest('button');
            button.classList.add('loading');
            button.disabled = true;

            // Simular una llamada AJAX (en una implementación real, usar fetch o axios)
            setTimeout(() => {
                // En una implementación real, esto sería una llamada AJAX
                alert('Diagnóstico marcado como resuelto. La página se recargará.');
                window.location.reload();
            }, 1000);
        }
    };

    // Función para generar orden de trabajo
    window.generateWorkOrder = function(diagnosticId) {
        if (confirm('¿Desea generar una orden de trabajo para este diagnóstico?')) {
            const button = event.target.closest('button');
            button.classList.add('loading');
            button.disabled = true;

            // Simular una llamada AJAX
            setTimeout(() => {
                alert('Orden de trabajo generada exitosamente. Redirigiendo...');
                // En una implementación real, redirigir a la página de la OT
                window.location.reload();
            }, 1000);
        }
    };

    // Función para imprimir diagnóstico
    window.printDiagnostic = function() {
        window.print();
    };

    // Función para eliminar diagnóstico
    window.deleteDiagnostic = function(diagnosticId) {
        const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
        modal.show();
    };

    // Función para confirmar eliminación
    window.confirmDelete = function() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
        modal.hide();

        // Simular eliminación
        setTimeout(() => {
            alert('Diagnóstico eliminado exitosamente. Redirigiendo a la lista...');
            window.location.href = '/diagnostics/'; // Ajustar URL según sea necesario
        }, 500);
    };

    // Función para formatear fechas de manera más legible
    function formatDates() {
        const dateElements = document.querySelectorAll('.text-muted');
        dateElements.forEach(element => {
            // Las fechas ya están formateadas en el template Django
            // Esta función puede usarse para formateo adicional si es necesario
        });
    }

    formatDates();

    // Función para resaltar información crítica
    function highlightCriticalInfo() {
        const criticalBadges = document.querySelectorAll('.badge.bg-danger');
        criticalBadges.forEach(badge => {
            if (badge.textContent.toLowerCase().includes('crítica')) {
                const card = badge.closest('.card');
                if (card) {
                    card.style.borderLeft = '4px solid #dc3545';
                }
            }
        });

        // Resaltar si afecta operaciones
        const affectsOperations = document.querySelector('.badge.bg-danger');
        if (affectsOperations && affectsOperations.textContent.includes('Afecta Operaciones')) {
            affectsOperations.style.animation = 'pulse 2s infinite';
        }
    }

    highlightCriticalInfo();

    // Función para agregar animación de pulso
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    // Función para manejar errores de carga de imágenes
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
        });
    });

    // Función para copiar información al portapapeles
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copiado al portapapeles', 'success');
        }, function(err) {
            console.error('Error al copiar: ', err);
            showToast('Error al copiar', 'error');
        });
    }

    // Función para mostrar toast de notificaciones
    function showToast(message, type) {
        // Crear elemento de toast si no existe
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Inicializar y mostrar toast
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();

            // Remover toast después de que se oculte
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        }
    }

    // Agregar funcionalidad de copiar al hacer clic en ciertos elementos
    const copyableElements = document.querySelectorAll('.stat-value, .badge');
    copyableElements.forEach(element => {
        element.style.cursor = 'pointer';
        element.title = 'Click para copiar';
        element.addEventListener('click', function() {
            copyToClipboard(this.textContent.trim());
        });
    });

    // Función para expandir/colapsar secciones largas
    function makeSectionsCollapsible() {
        const sections = document.querySelectorAll('.card-body p.text-muted');
        sections.forEach(section => {
            if (section.textContent.length > 200) {
                const originalText = section.textContent;
                const truncatedText = originalText.substring(0, 200) + '...';

                section.textContent = truncatedText;
                section.style.cursor = 'pointer';
                section.title = 'Click para expandir';

                let isExpanded = false;
                section.addEventListener('click', function() {
                    if (isExpanded) {
                        this.textContent = truncatedText;
                        this.title = 'Click para expandir';
                    } else {
                        this.textContent = originalText;
                        this.title = 'Click para colapsar';
                    }
                    isExpanded = !isExpanded;
                });
            }
        });
    }

    makeSectionsCollapsible();

    // Función para validar estado del diagnóstico y mostrar acciones apropiadas
    function validateDiagnosticState() {
        const statusBadge = document.querySelector('.badge.bg-success, .badge.bg-warning, .badge.bg-info, .badge.bg-secondary');
        if (statusBadge) {
            const status = statusBadge.textContent.trim().toLowerCase();

            // Ocultar acciones inapropiadas basadas en el estado
            const resolveButton = document.querySelector('button[onclick*="markAsResolved"]');
            const workOrderButton = document.querySelector('button[onclick*="generateWorkOrder"]');

            if (status.includes('resuelta') && resolveButton) {
                resolveButton.style.display = 'none';
            }

            if (!status.includes('diagnóstico in situ') && workOrderButton) {
                workOrderButton.style.display = 'none';
            }
        }
    }

    validateDiagnosticState();

    // Función para manejar navegación por teclado
    document.addEventListener('keydown', function(e) {
        // Ctrl+P para imprimir
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            printDiagnostic();
        }

        // Escape para volver a la lista
        if (e.key === 'Escape') {
            const backButton = document.querySelector('a[href*="diagnostics_list"]');
            if (backButton) {
                window.location.href = backButton.href;
            }
        }
    });

    // Función para actualizar el tiempo transcurrido en tiempo real
    function updateElapsedTime() {
        const timeElement = document.querySelector('.stat-value');
        if (timeElement && timeElement.textContent.includes('ago')) {
            // En una implementación real, esto actualizaría el tiempo cada minuto
            setTimeout(updateElapsedTime, 60000); // Actualizar cada minuto
        }
    }

    updateElapsedTime();

    // Función para manejar cambios de tamaño de ventana
    window.addEventListener('resize', function() {
        // Ajustar elementos responsive si es necesario
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            // Ajustes específicos para móviles
            if (window.innerWidth < 768) {
                card.classList.add('mb-3');
            } else {
                card.classList.remove('mb-3');
            }
        });
    });

    // Ejecutar ajustes iniciales de responsive
    window.dispatchEvent(new Event('resize'));
});