// Inicializar modal
const modalEl = document.getElementById("modalFormulario");
const modal = new bootstrap.Modal(modalEl);

// Abrir modal
document.getElementById("btnAbrirFormulario").addEventListener("click", () => {
    modal.show();
});

// Manejo del formulario
document.getElementById("formObservacion").addEventListener("submit", async function(e) {
    e.preventDefault();
    const formData = new FormData(this);

    try {
        const response = await fetch("/administrador/observador/registrar", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.status === "ok") {
            alert(result.message);
            modal.hide(); // Cierra el modal correctamente
            location.reload(); // Recarga la página si quieres actualizar la tabla
        } else {
            alert("Error al guardar la observación");
        }
    } catch (error) {
        console.error(error);
        alert("Error al conectar con el servidor");
    }
});