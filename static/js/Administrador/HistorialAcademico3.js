document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const historialId = params.get('historial_id'); 
    
    const API_URL_NOTAS = `/administrador/api/historialacademico/notas/${historialId}`; 
    
    // Elementos del DOM a rellenar
    const nombreEstudianteElement = document.querySelector('.d-flex h5');
    const cursoElement = document.querySelector('.d-flex span');
    const tituloPeriodoElement = document.querySelector('.descripcion');
    const tbodyNotas = document.querySelector('.card:nth-child(2) table tbody');
    const tbodyRecuperaciones = document.querySelector('.card:nth-child(3) table tbody');
    
    const COLUMNS_COUNT = 7; // Nueva cuenta de columnas para la tabla de Notas

    if (!historialId) {
        alert("Error: ID de historial no proporcionado. Regresando a selección.");
        return;
    }

    // Función para rellenar la tabla de notas (ACTUALIZADA)
    function rellenarTablaNotas(notas) {
        tbodyNotas.innerHTML = ''; // Limpiar tabla
        if (notas.length === 0) {
            tbodyNotas.innerHTML = `<tr><td colspan="${COLUMNS_COUNT}" class="text-center">No hay notas registradas para este periodo.</td></tr>`;
            return;
        }

        notas.forEach(n => {
            const row = tbodyNotas.insertRow();
            row.insertCell().textContent = n.Materia;
            // Usamos .toFixed(2) para mejor precisión, pero puedes ajustarlo
            row.insertCell().textContent = (n.Nota1 || 0).toFixed(2);
            row.insertCell().textContent = (n.Nota2 || 0).toFixed(2);
            row.insertCell().textContent = (n.Nota3 || 0).toFixed(2);
            row.insertCell().textContent = (n.Nota4 || 0).toFixed(2); // NUEVA COLUMNA
            row.insertCell().textContent = (n.Promedio || 0).toFixed(2); // NUEVA COLUMNA (Promedio Detalle)
            row.insertCell().textContent = (n.NotaFinal || 0).toFixed(2); // NUEVA COLUMNA (Promedio General)
        });
    }

    // Función para rellenar la tabla de recuperaciones (SIN CAMBIOS)
    function rellenarTablaRecuperaciones(recuperaciones) {
        tbodyRecuperaciones.innerHTML = ''; // Limpiar tabla
        if (recuperaciones.length === 0) {
            tbodyRecuperaciones.innerHTML = '<tr><td colspan="3" class="text-center">No hay recuperaciones pendientes o registradas.</td></tr>';
            return;
        }

        recuperaciones.forEach(r => {
            const row = tbodyRecuperaciones.insertRow();
            row.insertCell().textContent = r.Materia;
            row.insertCell().textContent = r.Observacion;
            row.insertCell().textContent = r.NotaRecuperacion || ''; 
        });
    }


    async function cargarDetalleHistorialNotas() {
        try {
            const response = await fetch(API_URL_NOTAS);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "No se pudo cargar el detalle del historial académico.");
            }
            const data = await response.json();
            
            // 1. Actualizar el encabezado y títulos
            nombreEstudianteElement.textContent = data.EstudianteNombre;
            cursoElement.textContent = data.Curso;
            tituloPeriodoElement.textContent = `Historial Académico - Periodo ${data.Periodo} (${data.Anio})`;
            
            // 2. Rellenar las tablas
            rellenarTablaNotas(data.Notas);
            rellenarTablaRecuperaciones(data.Recuperaciones);

        } catch (error) {
            console.error('Error al cargar detalle de notas:', error);
            alert(`Error de carga: ${error.message}`);
            // Limpiar tablas si falla la carga
            tbodyNotas.innerHTML = `<tr><td colspan="${COLUMNS_COUNT}" class="text-center text-danger">Error al cargar datos.</td></tr>`;
            tbodyRecuperaciones.innerHTML = '<tr><td colspan="3" class="text-center text-danger">Error al cargar datos.</td></tr>';
        }
    }

    cargarDetalleHistorialNotas();
});