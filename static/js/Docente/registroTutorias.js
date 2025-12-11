// registroTutorias.js

document.addEventListener("DOMContentLoaded", () => {
    // Referencias a elementos clave
    const form = document.getElementById("formRegistroTutoria");
    // Referencia al <tbody> de la tabla que creamos en el HTML
    const tablaCuerpo = document.getElementById("tablaCuerpoTutorias"); 
    const btnGuardar = document.getElementById("btnGuardarTutoria");
    // Inicializar el modal de Bootstrap (requiere el JS de Bootstrap)
    const modalElement = document.getElementById('modalTutoria');
    const modal = new bootstrap.Modal(modalElement);
    
    // Función para obtener el valor del <select> de Curso
    function getCursoValue() {
        // Usamos el ID 'curso-select' que añadimos en el HTML
        const selectCurso = document.getElementById("curso-select");
        return selectCurso ? selectCurso.value : '';
    }

    // --- Función para agregar la fila al historial visual ---
    function agregarFilaATabla(t) {
        let fila = document.createElement("tr");
        fila.innerHTML = `
            <td>${t.nombre || ''}</td>
            <td>${t.rol || ''}</td>
            <td>${t.tema || ''}</td>
            <td>${t.fecha || ''}</td>
            <td>${t.curso || ''}</td>
            <td>${t.estudiante || ''}</td>
            <td>${t.correo || ''}</td>
            <td>${t.motivo || ''}</td>
            <td>${t.observaciones || ''}</td>
            <td><button class="btn btn-danger btn-sm eliminar-btn" data-id="${t.id || ''}"><i class="bi bi-trash3-fill"></i></button></td>
        `;
        
        // Agregar la nueva fila al principio de la tabla (las más recientes primero)
        tablaCuerpo.prepend(fila); 
    }
    
    // --- Cargar Tutorías Iniciales desde la Base de Datos ---
    async function cargarTutorias() {
        try {
            // Llama a la ruta de Flask para obtener el historial
            const res = await fetch("/docente/tutorias/historial"); 
            
            if (!res.ok) {
                 throw new Error(`Error ${res.status}: Fallo al cargar el historial.`);
            }
            
            const data = await res.json();
            
            if (data.success) {
                // Limpiar SOLO el cuerpo de la tabla (no el thead)
                tablaCuerpo.innerHTML = ''; 
                // data.tutorias viene ordenado por el backend
                (data.tutorias || []).forEach(agregarFilaATabla);
            } else {
                console.error("No se pudo cargar el historial de tutorías:", data.error);
            }
        } catch (err) {
            console.error("Error al obtener tutorías del servidor:", err);
            tablaCuerpo.innerHTML = `<tr><td colspan="10" class="text-center text-danger">⚠️ Error al cargar tutorías. ${err.message}</td></tr>`;
        }
    }

    // Cargar los datos de la BD al cargar la página
    cargarTutorias();
    
    // --- Enviar los datos a Flask (Fetch/AJAX) ---
    btnGuardar.addEventListener("click", async (e) => {
        // El botón está fuera del <form>, así que validamos manualmente
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        btnGuardar.disabled = true;

        const tutoria = {
            nombre: document.getElementById("nombre").value,
            rol: document.getElementById("rol").value,
            tema: document.getElementById("Tema").value,
            fecha: document.getElementById("fecha").value,
            curso: getCursoValue(), 
            estudiante: document.getElementById("nombre_estudiante").value,
            correo: document.getElementById("correo").value,
            motivo: document.getElementById("motivo").value,
            observaciones: document.getElementById("observaciones").value 
        };

        try {
            const res = await fetch("/docente/tutorias/registro", { 
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(tutoria),
            });
            
            if (!res.ok) {
                const textError = await res.text();
                throw new Error(`Fallo del Servidor (${res.status}): ${textError.substring(0, 100)}...`);
            }

            const data = await res.json();

            if (data.success) {
                // 1. Agregar la fila a la tabla (la BD debe devolver el objeto 'tutoria')
                agregarFilaATabla(data.tutoria);
                
                // 2. Ocultar el modal y limpiar
                modal.hide(); 
                form.reset(); 
                alert("✅ Tutoría registrada con éxito.");
                
            } else {
                alert("❌ Error al guardar en la BD: " + (data.error || "Error de servidor desconocido."));
            }

        } catch (err) {
            console.error("Error de conexión o servidor:", err);
            alert("🛑 Error crítico al enviar datos: " + err.message);
        } finally {
            btnGuardar.disabled = false;
        }
    });

    // Opcional: Limpiar la validación del formulario al cerrar el modal
    modalElement.addEventListener('hidden.bs.modal', () => {
        form.classList.remove('was-validated'); 
        form.reset();
    });
});