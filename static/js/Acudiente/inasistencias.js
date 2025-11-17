const form = document.getElementById("justificacionForm");
const formMessage = document.getElementById("formMessage");
const clearBtn = document.getElementById("clearBtn");

// === Enviar excusa al servidor ===
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const studentName = form.studentName.value.trim();
    const relation = form.relation.value.trim();
    const date = form.date.value;
    const reason = form.reason.value.trim();
    const evidence = form.evidence.files[0];

    // Validación
    if (!studentName || !relation || !date || !reason) {
        formMessage.textContent = "Por favor completa todos los campos obligatorios.";
        formMessage.style.color = "red";
        return;
    }

    // === Preparar datos con archivo ===
    const formData = new FormData();
    formData.append("studentName", studentName);
    formData.append("relation", relation);
    formData.append("date", date);
    formData.append("reason", reason);
    if (evidence) formData.append("evidence", evidence);

    try {
        const response = await fetch("/api/excusas", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            formMessage.textContent = data.error || "Error al enviar la excusa.";
            formMessage.style.color = "red";
            return;
        }

        // Éxito
        formMessage.textContent = "Justificación enviada correctamente. El docente fue notificado.";
        formMessage.style.color = "green";

        form.reset();

    } catch (error) {
        console.error(error);
        formMessage.textContent = "Error inesperado. Intenta nuevamente.";
        formMessage.style.color = "red";
    }
});

// === Botón limpiar ===
clearBtn.addEventListener("click", () => {
    form.reset();
    formMessage.textContent = "";
});
