// Script simple para debug
console.log("DEBUG: Script cargado");

document.addEventListener('DOMContentLoaded', function() {
    console.log("DEBUG: DOM cargado");
    
    // Verificar si existe el formPeriodos
    const formPeriodos = document.getElementById('formPeriodos');
    console.log("DEBUG: formPeriodos encontrado:", formPeriodos);
    
    if (formPeriodos) {
        console.log("DEBUG: Contenido actual de formPeriodos:", formPeriodos.innerHTML.substring(0, 200));
    }
});

// También intentar cargar asignaturas
async function cargarAsignaturasDisponibles() {
    console.log("DEBUG: Iniciando carga de asignaturas...");
    try {
        const response = await fetch('/acudiente/api/asignaturas_disponibles');
        console.log("DEBUG: Response status:", response.status);
        
        if (!response.ok) {
            console.error("DEBUG: Error en la respuesta");
            return;
        }
        
        const asignaturas = await response.json();
        console.log("DEBUG: Asignaturas recibidas:", asignaturas);
        
    } catch (error) {
        console.error('DEBUG: Error al cargar asignaturas:', error);
    }
}

// Llamar a la función directamente también
console.log("DEBUG: Llamando directamente a la función");
cargarAsignaturasDisponibles();