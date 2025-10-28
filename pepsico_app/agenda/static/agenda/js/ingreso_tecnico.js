// ingreso_tecnico.js - Funcionalidad para captura de fotos técnicas de ingreso existente

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const camera = document.getElementById('camera');
    const canvas = document.getElementById('canvas');
    const takePhotoBtns = document.querySelectorAll('.take-photo-btn');
    const submitBtn = document.getElementById('submit-btn');
    const photoForm = document.getElementById('photo-form');

    // Variables de estado
    let stream = null;
    let capturedPhotos = new Array(7).fill(null); // 7 fotos requeridas

    // Inicializar eventos
    takePhotoBtns.forEach((btn, index) => {
        btn.addEventListener('click', () => takePhoto(index));
    });
    photoForm.addEventListener('submit', submitForm);

    // Iniciar la cámara automáticamente
    startCamera();

    // Función para iniciar la cámara
    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Usar cámara trasera si está disponible
                }
            });

            camera.srcObject = stream;
        } catch (error) {
            console.error('Error accediendo a la cámara:', error);
            showError('No se pudo acceder a la cámara. Verifique los permisos del navegador.');
        }
    }

    // Función para mostrar errores
    function showError(message) {
        // Remover error anterior si existe
        const existingError = document.querySelector('.alert-danger');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;

        const formSection = document.querySelector('.photo-capture-section');
        formSection.insertBefore(errorDiv, formSection.firstChild);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    // Función para capturar foto
    function takePhoto(index) {
        if (!camera.videoWidth) {
            showError('La cámara no está lista aún');
            return;
        }

        // Configurar canvas
        canvas.width = camera.videoWidth;
        canvas.height = camera.videoHeight;

        // Dibujar la imagen del video en el canvas
        const ctx = canvas.getContext('2d');
        ctx.drawImage(camera, 0, 0, canvas.width, canvas.height);

        // Convertir a blob
        canvas.toBlob((blob) => {
            const file = new File([blob], `photo_${index}.jpg`, { type: 'image/jpeg' });

            // Crear input hidden para el archivo
            const inputName = `photo_${index}`;
            let input = document.querySelector(`input[name="${inputName}"]`);

            if (!input) {
                input = document.createElement('input');
                input.type = 'file';
                input.name = inputName;
                input.style.display = 'none';
                photoForm.appendChild(input);
            }

            // Crear FileList simulada
            const dt = new DataTransfer();
            dt.items.add(file);
            input.files = dt.files;

            // Guardar referencia de la foto capturada
            capturedPhotos[index] = {
                file: file,
                url: canvas.toDataURL('image/jpeg')
            };

            updatePhotoItems();
            checkAllPhotosCaptured();
        }, 'image/jpeg', 0.8);
    }

    // Función para actualizar la visualización de las fotos
    function updatePhotoItems() {
        takePhotoBtns.forEach((btn, index) => {
            const photoItem = btn.closest('.photo-item');

            if (capturedPhotos[index]) {
                // Foto capturada
                photoItem.classList.add('captured');

                // Crear o actualizar preview
                let preview = photoItem.querySelector('.photo-preview');
                if (!preview) {
                    preview = document.createElement('div');
                    preview.className = 'photo-preview';
                    photoItem.insertBefore(preview, btn);
                }

                preview.innerHTML = `
                    <img src="${capturedPhotos[index].url}" alt="Foto ${index + 1}">
                `;

                btn.innerHTML = '<i class="fas fa-retake"></i> Recapturar';
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-warning');

            } else {
                // Foto no capturada
                photoItem.classList.remove('captured');
                const preview = photoItem.querySelector('.photo-preview');
                if (preview) {
                    preview.remove();
                }

                btn.innerHTML = '<i class="fas fa-camera"></i> Capturar';
                btn.classList.remove('btn-warning');
                btn.classList.add('btn-primary');
            }
        });
    }

    // Función para verificar si todas las fotos están capturadas
    function checkAllPhotosCaptured() {
        const allCaptured = capturedPhotos.every(photo => photo !== null);
        submitBtn.disabled = !allCaptured;

        if (allCaptured) {
            submitBtn.innerHTML = '<i class="fas fa-save"></i> Registrar Ingreso Técnico';
        } else {
            const capturedCount = capturedPhotos.filter(photo => photo !== null).length;
            submitBtn.innerHTML = `<i class="fas fa-save"></i> Registrar Ingreso Técnico (${capturedCount}/7 fotos)`;
        }
    }

    // Función para enviar el formulario
    function submitForm(e) {
        // Verificar que todas las fotos estén capturadas
        if (capturedPhotos.some(photo => photo === null)) {
            e.preventDefault();
            showError('Debe capturar todas las fotos requeridas antes de continuar');
            return;
        }

        // Detener la cámara antes de enviar
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        // El formulario se enviará normalmente
    }

    // Limpiar recursos cuando se cierra la página
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
});