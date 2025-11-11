document.addEventListener('DOMContentLoaded', () => {
    const btnBuscar = document.getElementById('btnBuscar');
    // Asumo que el input de documento tiene la clase 'custom-input'
    const inputDocumento = document.querySelector('.search-container .custom-input'); 
    
    const API_URL_BUSCAR_BASE = '/administrador/api/historialacademico/buscar_documento/'; 
    const BASE_URL_NEXT = btnBuscar.dataset.url; // url_for('Administrador.historialacademico2')

    btnBuscar.addEventListener('click', async (e) => {
        e.preventDefault(); 
        const documento = inputDocumento.value.trim();

        if (!documento) {
            alert("Por favor, ingrese el número de documento del estudiante.");
            return;
        }

        try {
            const response = await fetch(API_URL_BUSCAR_BASE + documento);
            
            if (!response.ok) {
                alert("Estudiante no encontrado o sin matrícula activa.");
                return;
            }

            const estudianteData = await response.json();
            const idMatricula = estudianteData.ID_Matricula_Reciente;
            
            if (idMatricula) {
                // Redirigir a historialacademico2, enviando el ID_Matricula en la URL
                window.location.href = `${BASE_URL_NEXT}?matricula_id=${idMatricula}`;
            } else {
                alert("Estudiante encontrado, pero no se pudo obtener el ID de matrícula.");
            }

        } catch (error) {
            console.error('Error al buscar estudiante:', error);
            alert("Error de conexión al buscar el estudiante.");
        }
    });
});