let cameraStream = null;
let capturedImages = [];

const cameraPreview = document.getElementById('camera-preview');
const cameraCanvas = document.getElementById('camera-canvas');
const startCameraBtn = document.getElementById('start-camera');
const capturePhotoBtn = document.getElementById('capture-photo');
const stopCameraBtn = document.getElementById('stop-camera');
const capturedImagesContainer = document.getElementById('captured-images');
const cameraImagesInput = document.getElementById('camera-images-input');

// Función para iniciar la cámara
async function startCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }, // Cámara trasera si está disponible
            audio: false
        });

        cameraPreview.srcObject = cameraStream;
        cameraPreview.style.display = 'block';
        startCameraBtn.style.display = 'none';
        capturePhotoBtn.style.display = 'inline-block';
        stopCameraBtn.style.display = 'inline-block';

    } catch (error) {
        console.error('Error al acceder a la cámara:', error);
        alert('No se pudo acceder a la cámara. Verifique los permisos.');
    }
}

// Función para detener la cámara
function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }

    cameraPreview.style.display = 'none';
    cameraPreview.srcObject = null;
    startCameraBtn.style.display = 'inline-block';
    capturePhotoBtn.style.display = 'none';
    stopCameraBtn.style.display = 'none';
}

// Función para capturar foto
function capturePhoto() {
    const context = cameraCanvas.getContext('2d');
    cameraCanvas.width = cameraPreview.videoWidth;
    cameraCanvas.height = cameraPreview.videoHeight;
    context.drawImage(cameraPreview, 0, 0);

    // Convertir canvas a blob y crear un archivo
    cameraCanvas.toBlob((blob) => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const fileName = `foto_${timestamp}.jpg`;
        const file = new File([blob], fileName, { type: 'image/jpeg' });

        const imageData = {
            id: Date.now(),
            file: file,
            url: URL.createObjectURL(blob)
        };

        capturedImages.push(imageData);
        updateCapturedImagesDisplay();
        updateFormData();
    }, 'image/jpeg', 0.8);
}

// Función para actualizar la visualización de imágenes capturadas
function updateCapturedImagesDisplay() {
    capturedImagesContainer.innerHTML = '';

    capturedImages.forEach((image, index) => {
        const imageDiv = document.createElement('div');
        imageDiv.className = 'image-preview';

        const img = document.createElement('img');
        img.src = image.url;
        img.alt = `Foto ${index + 1}`;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'remove-image';
        removeBtn.innerHTML = '×';
        removeBtn.onclick = () => removeImage(index);

        imageDiv.appendChild(img);
        imageDiv.appendChild(removeBtn);
        capturedImagesContainer.appendChild(imageDiv);
    });
}

// Función para remover imagen
function removeImage(index) {
    URL.revokeObjectURL(capturedImages[index].url);
    capturedImages.splice(index, 1);
    updateCapturedImagesDisplay();
    updateFormData();
}

// Función para actualizar los datos del formulario
function updateFormData() {
    // Crear un DataTransfer para agregar los archivos al input
    const dt = new DataTransfer();

    capturedImages.forEach((image, index) => {
        // Mantener el archivo original
        dt.items.add(image.file);
    });

    // Asignar los archivos al input
    cameraImagesInput.files = dt.files;
}

// Event listeners
startCameraBtn.addEventListener('click', startCamera);
capturePhotoBtn.addEventListener('click', capturePhoto);
stopCameraBtn.addEventListener('click', stopCamera);

// Obtener coordenadas GPS automáticamente
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                document.getElementById('id_latitude').value = position.coords.latitude;
                document.getElementById('id_longitude').value = position.coords.longitude;
            },
            (error) => {
                console.warn('Error obteniendo ubicación:', error.message);
                // No alertar, solo loggear
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutos
            }
        );
    } else {
        console.warn('Geolocalización no soportada');
    }
}

// Obtener ubicación al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    getLocation();
    
    // Debug: Verificar que los checkboxes existen y son funcionales
    const emergencyCheckbox = document.getElementById('id_is_emergency');
    const towCheckbox = document.getElementById('id_requires_tow');
    
    if (emergencyCheckbox) {
        console.log('Checkbox is_emergency encontrado:', emergencyCheckbox.checked);
        emergencyCheckbox.addEventListener('change', function() {
            console.log('is_emergency cambió a:', this.checked);
        });
    } else {
        console.warn('Checkbox is_emergency NO encontrado');
    }
    
    if (towCheckbox) {
        console.log('Checkbox requires_tow encontrado:', towCheckbox.checked);
        towCheckbox.addEventListener('change', function() {
            console.log('requires_tow cambió a:', this.checked);
        });
    } else {
        console.warn('Checkbox requires_tow NO encontrado');
    }
});

// Limpiar recursos cuando se cierra la página
window.addEventListener('beforeunload', () => {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
    }
    capturedImages.forEach(img => URL.revokeObjectURL(img.url));
});