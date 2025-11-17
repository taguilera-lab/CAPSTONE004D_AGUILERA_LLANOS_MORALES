// Función para inicializar el botón de diagnóstico
function initDiagnosticoButton(ingresoId, ingresoPatent) {
    const btnDiagnostico = document.querySelector('.btn-diagnostico');
    if (btnDiagnostico) {
        btnDiagnostico.addEventListener('click', function() {
            // Mostrar indicador de carga
            btnDiagnostico.disabled = true;
            btnDiagnostico.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';

            // Crear diagnóstico en blanco automáticamente
            fetch(`/diagnostics/crear/?from_ingreso=${ingresoId}&auto_create=true`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    'severity': 'Sin especificar',
                    'category': 'Mantenimiento',
                    'symptoms': 'Diagnóstico inicial del ingreso técnico',
                    'location': `Ingreso Técnico - Vehículo ${ingresoPatent}`,
                    'status': 'Reportada'
                })
            })
            .then(response => {
                if (response.ok) {
                    // Redirigir a la lista de diagnósticos
                    window.location.href = '/diagnostics/';
                } else {
                    throw new Error('Error al crear diagnóstico');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al crear el diagnóstico. Intente nuevamente.');
                // Restaurar botón
                btnDiagnostico.disabled = false;
                btnDiagnostico.innerHTML = '<i class="fas fa-stethoscope"></i> Realizar Diagnóstico sin Incidentes';
            });
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Esta función será llamada desde el template con los parámetros necesarios
});