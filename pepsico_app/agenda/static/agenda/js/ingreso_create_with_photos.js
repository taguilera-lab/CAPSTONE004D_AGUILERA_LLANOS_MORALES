// JavaScript para ingreso_create_with_photos.html
// Maneja la captura manual de fotos usando la cámara del dispositivo

class PhotoCaptureManager {
    constructor(scheduleId) {
        this.scheduleId = scheduleId;
        this.video = document.getElementById(`video-${scheduleId}`);
        this.canvas = document.getElementById(`canvas-${scheduleId}`);
        this.photosGrid = document.getElementById(`photos-${scheduleId}`);
        this.cameraContainer = document.getElementById(`camera-${scheduleId}`);
        this.stream = null;
        this.capturedPhotos = [];
    }

    async startCamera() {
        try {
            // Solicitar acceso a la cámara trasera si está disponible
            const constraints = {
                video: {
                    facingMode: { ideal: 'environment' }, // Cámara trasera
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            this.cameraContainer.style.display = 'block';

            // Cambiar botones
            document.querySelector(`#form-${this.scheduleId} .btn-capture`).style.display = 'none';
            document.querySelector(`#form-${this.scheduleId} .btn-stop`).style.display = 'inline-block';

            // La captura automática se ha removido - ahora solo se toma foto al hacer clic

        } catch (error) {
            console.error('Error al acceder a la cámara:', error);
            alert('No se pudo acceder a la cámara. Verifique los permisos.');
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        this.video.srcObject = null;
        this.cameraContainer.style.display = 'none';

        // Cambiar botones
        document.querySelector(`#form-${this.scheduleId} .btn-capture`).style.display = 'inline-block';
        document.querySelector(`#form-${this.scheduleId} .btn-stop`).style.display = 'none';
    }

    takePhoto() {
        if (!this.stream) return;

        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;

        // Dibujar el frame actual del video en el canvas
        context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

        // Convertir a blob
        this.canvas.toBlob((blob) => {
            const photoData = {
                blob: blob,
                url: URL.createObjectURL(blob),
                timestamp: new Date().toLocaleString('es-ES'),
                id: Date.now()
            };

            this.capturedPhotos.push(photoData);
            this.displayPhoto(photoData);
            this.updateFormInput();
        }, 'image/jpeg', 0.8);
    }

    displayPhoto(photoData) {
        const photoItem = document.createElement('div');
        photoItem.className = 'photo-item';
        photoItem.dataset.photoId = photoData.id;

        photoItem.innerHTML = `
            <img src="${photoData.url}" alt="Foto ${photoData.timestamp}" class="photo-preview">
            <button type="button" class="photo-remove" onclick="photoManagers[${this.scheduleId}].removePhoto(${photoData.id})">
                ×
            </button>
        `;

        this.photosGrid.appendChild(photoItem);
    }

    removePhoto(photoId) {
        // Remover de la lista de fotos capturadas
        this.capturedPhotos = this.capturedPhotos.filter(photo => photo.id !== photoId);

        // Remover del DOM
        const photoItem = this.photosGrid.querySelector(`[data-photo-id="${photoId}"]`);
        if (photoItem) {
            photoItem.remove();
        }

        // Actualizar input del formulario
        this.updateFormInput();
    }

    updateFormInput() {
        const input = document.getElementById(`images-${this.scheduleId}`);

        // Crear un DataTransfer para manejar múltiples archivos
        const dt = new DataTransfer();

        this.capturedPhotos.forEach((photo, index) => {
            // Crear un archivo desde el blob
            const file = new File([photo.blob], `photo_${index + 1}_${photo.timestamp.replace(/[/:\s]/g, '_')}.jpg`, {
                type: 'image/jpeg'
            });
            dt.items.add(file);
        });

        input.files = dt.files;
    }

    cancelForm() {
        if (confirm('¿Está seguro de que desea cancelar? Se perderán todas las fotos capturadas.')) {
            this.stopCamera();
            this.capturedPhotos = [];
            this.photosGrid.innerHTML = '';
            this.updateFormInput();
        }
    }
}

// Objeto global para manejar los managers de fotos
const photoManagers = {};

// Función para iniciar la cámara (llamada desde el HTML)
function startCamera(scheduleId) {
    if (!photoManagers[scheduleId]) {
        photoManagers[scheduleId] = new PhotoCaptureManager(scheduleId);
    }
    photoManagers[scheduleId].startCamera();
}

// Función para detener la cámara (llamada desde el HTML)
function stopCamera(scheduleId) {
    if (photoManagers[scheduleId]) {
        photoManagers[scheduleId].stopCamera();
    }
}

// Función para tomar foto manualmente (llamada desde el HTML)
function takePhoto(scheduleId) {
    if (photoManagers[scheduleId]) {
        photoManagers[scheduleId].takePhoto();
    }
}

// Función para cancelar formulario (llamada desde el HTML)
function cancelForm(scheduleId) {
    if (photoManagers[scheduleId]) {
        photoManagers[scheduleId].cancelForm();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Verificar soporte de la API de medios
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Su navegador no soporta acceso a la cámara. Use un navegador moderno como Chrome, Firefox o Safari.');
        return;
    }

    // Agregar validación antes de enviar formularios
    document.querySelectorAll('.ingreso-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const scheduleId = this.id.replace('form-', '');
            const manager = photoManagers[scheduleId];

            if (manager && manager.stream) {
                // Detener la cámara antes de enviar
                manager.stopCamera();
            }
        });
    });

    // Limpiar streams cuando se cierra la página
    window.addEventListener('beforeunload', function() {
        Object.values(photoManagers).forEach(manager => {
            if (manager.stream) {
                manager.stopCamera();
            }
        });
    });
});