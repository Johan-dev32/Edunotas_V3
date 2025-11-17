// HistorialAcademico2.js
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const matriculaId = params.get('matricula_id');
    
    const selectPeriodo = document.getElementById('select-periodo');
    const noHistorialMessage = document.getElementById('no-historial-message');

    // Asume que el prefijo es /administrador, ajústalo si es diferente
    const ADMIN_PREFIX = '/administrador'; 
    const API_URL_DATOS = `/administrador/api/historialacademico/datos_estudiante/${matriculaId}`;
    const API_URL_HISTORIAL = `/administrador/api/historialacademico/historiales/${matriculaId}`; 
    const BASE_URL_NEXT = selectPeriodo.dataset.url; // URL para HistorialAcademico3

    if (!matriculaId) {
        // Mejorar el manejo de errores
        alert("Error: ID de matrícula no encontrado en la URL. Volviendo a la búsqueda.");
        window.history.back();
        return;
    }

    // --- FUNCIÓN 1: Cargar Datos del Estudiante ---
    async function cargarDatosEstudiante() {
        // ... (código de fetch y asignación de innerHTML a los IDs) ...
        try {
            const response = await fetch(API_URL_DATOS);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Fallo al cargar datos del estudiante.");
            }
            const data = await response.json();

            // Asignación de valores a los inputs
            document.getElementById('estudiante-nombre').textContent = data.NombreCompleto;
            document.getElementById('estudiante-documento').textContent = data.NumeroDocumento;
            document.getElementById('estudiante-grado').textContent = data.Grado;
            document.getElementById('estudiante-curso').textContent = data.Curso;

        } catch (error) {
            console.error("Error al cargar datos del estudiante:", error);
            // Mostrar error visible en la UI
            document.getElementById('estudiante-nombre').value = `ERROR: ${error.message}`;
        }
    }

    // --- FUNCIÓN 2: Cargar Historiales Académicos (periodos) ---
    async function cargarHistoriales() {
        // ... (código para cargar el selectPeriodo con historiales) ...
        try {
            const response = await fetch(API_URL_HISTORIAL);
            if (!response.ok) {
                throw new Error("Fallo al cargar la lista de historiales.");
            }
            const historiales = await response.json();

            selectPeriodo.innerHTML = '';
            selectPeriodo.disabled = false;

            if (historiales.length === 0) {
                noHistorialMessage.classList.remove('d-none');
                selectPeriodo.innerHTML = '<option value="">Sin Historiales</option>';
                selectPeriodo.disabled = true;
                return;
            }

            selectPeriodo.innerHTML = '<option value="">Seleccione un Periodo</option>';
            
            historiales.forEach(h => {
                const option = document.createElement('option');
                option.value = h.ID_Historial;
                option.textContent = `Año ${h.Anio} - Periodo ${h.Periodo} (${h.Descripcion})`;
                selectPeriodo.appendChild(option);
            });

        } catch (error) {
            console.error("Error al cargar historiales:", error);
            selectPeriodo.innerHTML = '<option value="">Error de Carga</option>';
        }
    }

    // --- Manejar Redirección al Seleccionar Periodo ---
    selectPeriodo.addEventListener('change', () => {
        const idHistorialSeleccionado = selectPeriodo.value;
        if (idHistorialSeleccionado) {
            window.location.href = `${BASE_URL_NEXT}?historial_id=${idHistorialSeleccionado}`;
        }
    });

    // Iniciar la carga
    cargarDatosEstudiante();
    cargarHistoriales();
});