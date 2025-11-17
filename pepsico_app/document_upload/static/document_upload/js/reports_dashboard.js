// Agregar animación a los botones de descarga
document.addEventListener('DOMContentLoaded', function() {
    const downloadButtons = document.querySelectorAll('a[href*="generate_excel_report"]');

    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
            this.disabled = true;

            // Revertir después de 3 segundos (por si hay error)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });
});

// Función para generar reporte de productividad
function generarProductividad() {
    const periodoSelect = document.getElementById('periodo-productividad');
    if (!periodoSelect) {
        alert('Error: No se encontró el selector de período para productividad');
        return;
    }
    const periodo = periodoSelect.value;
    const button = document.querySelector('button[onclick="generarProductividad()"]');

    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
    button.disabled = true;

    // Construir URL con parámetro de período
    const url = `/document_upload/reports/generate/productividad/?periodo=${periodo}`;

    // Crear enlace temporal y hacer clic
    const link = document.createElement('a');
    link.href = url;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Revertir botón después de 3 segundos
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

// Función para generar reporte de tiempos y horas hombre
function generarTiemposHorasHombre() {
    const periodoSelect = document.getElementById('periodo-tiempos');
    const filtroSelect = document.getElementById('filtro-tiempos');
    
    if (!periodoSelect) {
        alert('Error: No se encontró el selector de período para tiempos');
        return;
    }
    if (!filtroSelect) {
        alert('Error: No se encontró el selector de filtro para tiempos');
        return;
    }
    
    const periodo = periodoSelect.value;
    const filtro = filtroSelect.value;
    const button = document.querySelector('button[onclick="generarTiemposHorasHombre()"]');

    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
    button.disabled = true;

    // Construir URL con parámetros
    const url = `/document_upload/reports/generate/tiempos_horas_hombre/?periodo=${periodo}&filtro=${filtro}`;

    // Crear enlace temporal y hacer clic
    const link = document.createElement('a');
    link.href = url;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Revertir botón después de 3 segundos
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}
// Función para generar reporte de repuestos utilizados
function generarRepuestosUtilizados() {
    const periodoSelect = document.getElementById("periodo-repuestos");
    const filtroSelect = document.getElementById("filtro-repuestos");
    const periodo = periodoSelect.value;
    const filtro = filtroSelect.value;
    const button = document.querySelector("button[onclick=\"generarRepuestosUtilizados()\"]");
    
    const originalText = button.innerHTML;
    button.innerHTML = "<i class=\"fas fa-spinner fa-spin\"></i> Generando...";
    button.disabled = true;
    
    // Construir URL con parámetros
    const url = `/document_upload/reports/generate/repuestos_utilizados/?periodo=${periodo}&filtro=${filtro}`;
    
    // Crear enlace temporal y hacer clic
    const link = document.createElement("a");
    link.href = url;
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Revertir botón después de 3 segundos
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

// Función para generar reporte de vehículos ingresados/salidos
function generarVehiculosIngresadosSalidos() {
    const periodoSelect = document.getElementById("periodo-vehiculos");
    const filtroSelect = document.getElementById("filtro-vehiculos");
    const periodo = periodoSelect.value;
    const filtro = filtroSelect.value;
    const button = document.querySelector("button[onclick=\"generarVehiculosIngresadosSalidos()\"]");
    
    const originalText = button.innerHTML;
    button.innerHTML = "<i class=\"fas fa-spinner fa-spin\"></i> Generando...";
    button.disabled = true;
    
    // Construir URL con parámetros
    const url = `/document_upload/reports/generate/vehiculos_ingresados_salidos/?periodo=${periodo}&filtro=${filtro}`;
    
    // Crear enlace temporal y hacer clic
    const link = document.createElement("a");
    link.href = url;
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Revertir botón después de 3 segundos
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

// Función para generar reporte de KPIs de Flota
function generarKPIsFlota() {
    const periodoSelect = document.getElementById('periodo-kpis');
    const periodo = periodoSelect.value;
    const button = document.querySelector('button[onclick="generarKPIsFlota()"]');
    
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
    button.disabled = true;
    
    // Construir URL con parámetro de período
    const url = `/document_upload/reports/generate/kpis_flota/?periodo=${periodo}`;
    
    // Crear enlace temporal y hacer clic
    const link = document.createElement('a');
    link.href = url;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Revertir botón después de 3 segundos
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}
