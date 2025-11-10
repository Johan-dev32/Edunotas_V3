// static/js/Docentes/RegistroNotas.js

// ... (inicio y funciones calcularPromedioFila y guardarNotas quedan iguales) ...

document.addEventListener('DOMContentLoaded', () => {
    // ... (Listeners de form submit y nota-input) ...
    
    const selectPeriodo = document.getElementById('periodo_select');
    const selectAsignatura = document.getElementById('asignatura_select');

    // 🛑 Listener para cargar notas cuando ambos selectores cambian
    if (selectPeriodo && selectAsignatura) {
        selectPeriodo.addEventListener('change', verificarYcargarNotas);
        selectAsignatura.addEventListener('change', verificarYcargarNotas);
    }
});

function verificarYcargarNotas() {
    const periodo = document.getElementById('periodo_select').value;
    const asignaturaId = document.getElementById('asignatura_select').value;
    
    // Solo cargamos si ambos selectores tienen valor seleccionado
    if (periodo && asignaturaId) {
        cargarNotasExistentes(periodo, asignaturaId);
    } else {
        limpiarInputsDeNotas();
    }
}

async function cargarNotasExistentes(periodo, asignaturaId) {
    // 1. Crear la URL de AJAX con los valores reales
    let url = URL_BASE_CARGAR_NOTAS.replace('/0/0', `/${asignaturaId}/${periodo}`);
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('No se pudieron cargar las notas.');
        }
        
        const notasEstudiantes = await response.json();
        
        // 2. Limpiar e insertar las notas en la tabla
        limpiarInputsDeNotas(); 
        
        notasEstudiantes.forEach(data => {
            const estudianteId = data.ID_Usuario;
            const notas = data.notas;
            const promedio = data.Promedio_Final;
            
            // a) Insertar notas en los inputs
            for (let i = 1; i <= 5; i++) {
                const inputName = `nota_${i}_${estudianteId}`;
                const input = document.querySelector(`input[name="${inputName}"]`);
                if (input && notas[`nota_${i}`] !== undefined) {
                    input.value = notas[`nota_${i}`];
                }
            }
            
            // b) Actualizar promedio final
            const promedioCell = document.getElementById(`promedio_final_${estudianteId}`);
            if (promedioCell) {
                promedioCell.textContent = promedio !== null ? promedio.toFixed(1) : 'N/A';
            }
        });

    } catch (error) {
        console.error('Error al cargar notas:', error);
        // Opcional: Mostrar un mensaje al usuario
    }
}

function limpiarInputsDeNotas() {
    document.querySelectorAll('#tablaNotas input[type="number"]').forEach(input => {
        input.value = '';
    });
    document.querySelectorAll('[id^="promedio_final_"]').forEach(cell => {
        cell.textContent = 'N/A';
    });
}

// ... (Ajustar guardarNotas para obtener el ID de la asignatura del selector) ...

async function guardarNotas() {
    const selectPeriodo = document.getElementById('periodo_select');
    const selectAsignatura = document.getElementById('asignatura_select');
    const periodo = selectPeriodo.value;
    const asignaturaId = selectAsignatura.value;

    if (!periodo || !asignaturaId) {
        alert('Por favor, seleccione Período y Asignatura.');
        return;
    }
    
    const form = document.getElementById('formRegistroNotas');
    const data = new FormData(form);
    
    try {
        // 🛑 Crear la URL de guardado con el ID de la asignatura seleccionada
        const url = URL_GUARDAR_NOTAS_BASE.replace('/0', `/${asignaturaId}`); 
        
        // ... (El resto de la lógica de fetch y manejo de respuesta es la misma) ...
        // ... (asegúrate de incluir el código de deshabilitar/habilitar el botón) ...

    } catch (error) {
        // ... (manejo de errores) ...
    }
}