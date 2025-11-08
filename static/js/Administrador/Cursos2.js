// static/js/Administrador/Cursos2.js

// 1. 🛑 Interceptor del Evento Submit (CRÍTICO para AJAX)
document.addEventListener('DOMContentLoaded', () => {
    console.log("Cursos2.js: Script cargado. Intentando adjuntar listener...");
    
    // Asegúrate de que el formulario en el HTML tiene id="formAsistencia"
    const formAsistencia = document.getElementById('formAsistencia');

    if (formAsistencia) {
        formAsistencia.addEventListener('submit', function(e) {
            console.log("✅ Evento 'submit' INTERCEPTADO.");
            e.preventDefault(); // Detiene el envío HTTP directo (adiós error 405)
            guardarAsistencia(); // Llama a la función que usa Fetch/AJAX
        });
    } else {
        console.error("❌ ERROR JS: El formulario con ID 'formAsistencia' no fue encontrado.");
    }
});

// 2. Función para manejar la petición AJAX
function guardarAsistencia() {
    // Verificamos que la URL haya sido inyectada desde Flask en el HTML
    if (typeof URL_GUARDAR_ASISTENCIA === 'undefined') {
        alert('❌ Error de configuración: La URL de guardado no está definida en el HTML.');
        return;
    }

    const form = document.getElementById('formAsistencia');
    const formData = new FormData(form);

    fetch(URL_GUARDAR_ASISTENCIA, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        // Log para depuración
        console.log(`Respuesta del servidor. Status: ${response.status}`);
        
        // Verifica si la respuesta es JSON antes de intentar parsear
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json();
        } else {
            // Si Flask devuelve un error HTML, lo capturamos aquí
            throw new Error(`Respuesta no es JSON. Status: ${response.status} URL: ${response.url}`);
        }
    })
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            // 🟢 Éxito: Llamamos al generador de PDF
            generarPDF(data.fecha); 
            
        } else if (data.status === 'error' && data.message.includes('ya fue tomada')) {
            // Manejo del error 409 (Duplicado)
            alert(`⚠️ Advertencia: ${data.message}`);
        } else {
            // Manejo de otros errores 'error' (ej. 500 de DB)
            alert(`❌ Error al guardar: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error de red o servidor en la petición AJAX:', error);
        alert(`❌ Fallo crítico de red/servidor. Revisa la Consola del navegador.`);
    });
}


// 3. Función para generar el PDF
// Asume que jsPDF y jspdf-autotable están cargados globalmente.
function generarPDF(fecha) {
    try {
        if (typeof window.jspdf === 'undefined' || typeof window.jspdf.jsPDF === 'undefined') {
            throw new Error("Librería jsPDF no cargada. Asegúrate de incluir los scripts en el HTML.");
        }
        
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('p', 'pt', 'letter'); 
        
        // 🛑 CRÍTICO: Debe ser el ID de la tabla de estudiantes
        const tabla = document.getElementById('tablaEstudiantes'); 
        
        // Aseguramos el nombre del curso
        const nombreCurso = typeof GRADO_GRUPO !== 'undefined' ? GRADO_GRUPO : "Curso Desconocido";
        const nombreArchivo = `Asistencia_${nombreCurso}_${fecha}.pdf`;
        
        // Contenido del PDF
        doc.setFontSize(16);
        doc.text("Reporte de Asistencia", 40, 50);
        doc.setFontSize(12);
        doc.text(`Curso: ${nombreCurso}`, 40, 70);
        doc.text(`Fecha: ${fecha}`, 40, 85);

        // Generar tabla
        doc.autoTable({
            html: tabla,
            startY: 100,
            theme: 'striped',
            headStyles: { 
                fillColor: [5, 7, 51], 
                textColor: 255 
            },
        });

        doc.save(nombreArchivo);
        console.log(`✅ PDF generado y descargado: ${nombreArchivo}`);
        
    } catch (e) {
        console.error("Error FATAL al generar PDF:", e);
        alert("⚠️ La asistencia se guardó, pero hubo un error crítico al generar el PDF.");
    }
}