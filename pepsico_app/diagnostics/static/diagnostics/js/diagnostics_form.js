// JavaScript para diagnostics_form.html
// Maneja la lógica del formulario de diagnósticos

document.addEventListener('DOMContentLoaded', function() {
    console.log('Diagnostics form loaded');

    // Inicializar validaciones del formulario
    initializeFormValidation();

    // Configurar cambios dinámicos en el formulario
    setupDynamicFields();

    // Configurar autocompletado si es necesario
    setupAutocomplete();
});

function initializeFormValidation() {
    const form = document.getElementById('diagnostics-form');

    if (form) {
        form.addEventListener('submit', function(e) {
            // Validaciones personalizadas antes del envío
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }

            // Mostrar indicador de carga
            showLoadingState();
        });
    }
}

function validateForm() {
    let isValid = true;
    const errors = [];

    // Validar que se haya seleccionado un mecánico si es requerido
    const assignedTo = document.getElementById('id_assigned_to');
    if (assignedTo && assignedTo.value === '') {
        errors.push('Debe seleccionar un mecánico asignado.');
        highlightField(assignedTo);
        isValid = false;
    }

    // Validar síntomas si se ha seleccionado severidad
    const severity = document.getElementById('id_severity');
    const symptoms = document.getElementById('id_symptoms');
    if (severity && severity.value && symptoms && symptoms.value.trim() === '') {
        errors.push('Los síntomas son obligatorios cuando se especifica una severidad.');
        highlightField(symptoms);
        isValid = false;
    }

    // Mostrar errores si existen
    if (errors.length > 0) {
        showErrors(errors);
    }

    return isValid;
}

function highlightField(field) {
    field.style.borderColor = '#dc3545';
    field.classList.add('is-invalid');

    // Remover el resaltado después de 3 segundos
    setTimeout(() => {
        field.style.borderColor = '';
        field.classList.remove('is-invalid');
    }, 3000);
}

function showErrors(errors) {
    // Remover errores anteriores
    const existingAlerts = document.querySelectorAll('.alert-danger');
    existingAlerts.forEach(alert => alert.remove());

    // Crear nueva alerta de error
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <strong>Errores en el formulario:</strong>
        <ul class="mb-0 mt-2">
            ${errors.map(error => `<li>${error}</li>`).join('')}
        </ul>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insertar al inicio del formulario
    const form = document.getElementById('diagnostics-form');
    form.insertBefore(alertDiv, form.firstChild);
}

function showLoadingState() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    }
}

function setupDynamicFields() {
    // Mostrar/ocultar campos de resolución según el estado
    const statusField = document.getElementById('id_status');
    const resolutionFields = document.querySelectorAll('[id^="id_resolution_"], #id_estimated_resolution_time');

    if (statusField && resolutionFields.length > 0) {
        function toggleResolutionFields() {
            const showResolution = ['Resuelta', 'OT_Generada'].includes(statusField.value);

            resolutionFields.forEach(field => {
                const formGroup = field.closest('.mb-3');
                if (formGroup) {
                    formGroup.style.display = showResolution ? 'block' : 'none';
                    field.required = showResolution;
                }
            });
        }

        statusField.addEventListener('change', toggleResolutionFields);
        toggleResolutionFields(); // Ejecutar al cargar
    }

    // Cambiar severidad automáticamente basada en síntomas
    const symptomsField = document.getElementById('id_symptoms');
    const severityField = document.getElementById('id_severity');

    if (symptomsField && severityField) {
        symptomsField.addEventListener('input', function() {
            const symptoms = this.value.toLowerCase();

            // Lógica simple para sugerir severidad
            if (symptoms.includes('grave') || symptoms.includes('critic') || symptoms.includes('peligro')) {
                if (severityField.value === '') {
                    severityField.value = 'Critica';
                }
            } else if (symptoms.includes('importante') || symptoms.includes('seri')) {
                if (severityField.value === '') {
                    severityField.value = 'Alta';
                }
            }
        });
    }
}

function setupAutocomplete() {
    // Configurar autocompletado para síntomas comunes
    const symptomsField = document.getElementById('id_symptoms');
    const possibleCausesField = document.getElementById('id_possible_cause');

    if (symptomsField) {
        let symptomsTimeout;
        symptomsField.addEventListener('input', function() {
            clearTimeout(symptomsTimeout);
            symptomsTimeout = setTimeout(() => {
                suggestCommonSymptoms(this.value);
            }, 500);
        });
    }

    if (possibleCausesField) {
        let causesTimeout;
        possibleCausesField.addEventListener('input', function() {
            clearTimeout(causesTimeout);
            causesTimeout = setTimeout(() => {
                suggestCommonCauses(this.value);
            }, 500);
        });
    }
}

function suggestCommonSymptoms(input) {
    // Lista de síntomas comunes para sugerencias
    const commonSymptoms = [
        'falla en el motor',
        'problemas de frenos',
        'dificultad para arrancar',
        'pérdida de potencia',
        'ruido extraño',
        'vibraciones',
        'problemas eléctricos',
        'falla en transmisión',
        'sobrecalentamiento',
        'pérdida de aceite'
    ];

    // Mostrar sugerencias si el input coincide
    const matchingSymptoms = commonSymptoms.filter(symptom =>
        symptom.toLowerCase().includes(input.toLowerCase()) && input.length > 2
    );

    showSuggestions(matchingSymptoms, 'symptoms');
}

function suggestCommonCauses(input) {
    // Lista de causas comunes para sugerencias
    const commonCauses = [
        'falla mecánica',
        'desgaste natural',
        'falta de mantenimiento',
        'problema eléctrico',
        'contaminación',
        'daño por impacto',
        'falla en sensor',
        'problema de combustible',
        'avería en sistema',
        'error de operador'
    ];

    // Mostrar sugerencias si el input coincide
    const matchingCauses = commonCauses.filter(cause =>
        cause.toLowerCase().includes(input.toLowerCase()) && input.length > 2
    );

    showSuggestions(matchingCauses, 'causes');
}

function showSuggestions(suggestions, type) {
    // Remover sugerencias anteriores
    const existingSuggestions = document.querySelector('.suggestions-list');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }

    if (suggestions.length === 0) return;

    // Crear lista de sugerencias
    const suggestionsList = document.createElement('ul');
    suggestionsList.className = 'suggestions-list list-group position-absolute';
    suggestionsList.style.cssText = 'z-index: 1000; max-height: 200px; overflow-y: auto;';

    suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.className = 'list-group-item list-group-item-action';
        li.textContent = suggestion;
        li.addEventListener('click', function() {
            const targetField = type === 'symptoms' ?
                document.getElementById('id_symptoms') :
                document.getElementById('id_possible_cause');

            if (targetField) {
                targetField.value = this.textContent;
                suggestionsList.remove();
                targetField.focus();
            }
        });
        suggestionsList.appendChild(li);
    });

    // Posicionar las sugerencias
    const targetField = type === 'symptoms' ?
        document.getElementById('id_symptoms') :
        document.getElementById('id_possible_cause');

    if (targetField) {
        const rect = targetField.getBoundingClientRect();
        suggestionsList.style.top = (rect.bottom + window.scrollY) + 'px';
        suggestionsList.style.left = (rect.left + window.scrollX) + 'px';
        suggestionsList.style.width = rect.width + 'px';

        document.body.appendChild(suggestionsList);

        // Cerrar sugerencias al hacer clic fuera
        document.addEventListener('click', function closeSuggestions(e) {
            if (!suggestionsList.contains(e.target) && e.target !== targetField) {
                suggestionsList.remove();
                document.removeEventListener('click', closeSuggestions);
            }
        });
    }
}

// Funciones de utilidad adicionales
function updateFieldVisibility() {
    // Lógica adicional para mostrar/ocultar campos según el estado del diagnóstico
    const status = document.getElementById('id_status')?.value;
    const resolutionSection = document.querySelector('.resolution-section');

    if (resolutionSection) {
        if (['Resuelta', 'OT_Generada'].includes(status)) {
            resolutionSection.style.display = 'block';
        } else {
            resolutionSection.style.display = 'none';
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('Diagnostics form JavaScript initialized');

    // Configurar validación en tiempo real
    setupRealTimeValidation();

    // Actualizar visibilidad inicial de campos
    updateFieldVisibility();
});

function setupRealTimeValidation() {
    // Validación en tiempo real para campos críticos
    const requiredFields = ['id_assigned_to', 'id_severity', 'id_status'];

    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('change', function() {
                if (this.value) {
                    this.classList.remove('is-invalid');
                    this.style.borderColor = '#28a745';
                } else {
                    this.classList.add('is-invalid');
                    this.style.borderColor = '#dc3545';
                }
            });
        }
    });
}