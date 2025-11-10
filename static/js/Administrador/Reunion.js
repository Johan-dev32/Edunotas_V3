document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formReunion");
    const linkGeneradoInput = document.getElementById("linkGenerado");
    const historial = document.getElementById("historial");
    const btnAgendar = document.getElementById("btnAgendar");

    const linkBase = "https://meet.google.com/landing";

    // Función para generar un ID único para el link de Meet
    function generarLinkUnico() {
        const uniqueId = Math.random().toString(36).substring(2, 10);
        linkGeneradoInput.value = `${linkBase}${uniqueId}`;
    }

    // --- Cargar Historial al Iniciar (Limitado a 3 en Python) ---
    function cargarHistorial() {
        fetch("/administrador/reuniones/historial") 
            .then(res => {
                if (!res.ok) {
                    throw new Error(`Error ${res.status}: Fallo al cargar el historial.`);
                }
                return res.json();
            })
            .then(data => {
                historial.innerHTML = "";
                // Como Python ya limita a 3 y ordena, solo los añadimos.
                (data || []).forEach(addReunionToHistorial);
            })
            .catch(err => {
                console.error("Error al cargar historial:", err);
                historial.innerHTML = `<li class="list-group-item list-group-item-danger">⚠️ Error al conectar con el servidor para obtener el historial.</li>`;
            });
    }

    // Cargar historial al cargar la página
    cargarHistorial();

    // --- Generar link ---
    btnAgendar.addEventListener("focus", generarLinkUnico);
    document.getElementById("invitados").addEventListener("blur", generarLinkUnico);


    // --- Interceptar el Submit y Guardar en BD ---
    form.addEventListener("submit", async e => {
        e.preventDefault();

        if (!linkGeneradoInput.value) {
             generarLinkUnico();
        }
        
        btnAgendar.disabled = true;

        const datosAEnviar = { 
            fecha: document.getElementById("fecha").value,
            tema: document.getElementById("tema").value,
            organizador: document.getElementById("organizador").value,
            cargo: document.getElementById("cargo").value,
            invitados: document.getElementById("invitados").value,
            link: linkGeneradoInput.value
        };

        try {
            const res = await fetch("/administrador/reuniones", { 
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datosAEnviar),
                credentials: "same-origin"
            });

            if (res.redirected) {
                window.location.href = res.url;
                return;
            }

            if (!res.ok) {
                 const textError = await res.text();
                 throw new Error(`Fallo del Servidor (${res.status}): ${textError.substring(0, 100)}...`);
            }
            
            const data = await res.json();

            if (data.success) {
                // 🚀 ÉXITO: Usamos los datos devueltos por el servidor (data.reunion)
                addReunionToHistorial(data.reunion); 
                
                form.reset();
                linkGeneradoInput.value = "";
                alert("✅ Reunión agendada y guardada en la base de datos.");
                window.open(datosAEnviar.link, "_blank"); 
                
            } else {
                alert("❌ Error al guardar en la BD: " + (data.error || "Desconocido. Revisa la consola del servidor."));
            }
        } catch (err) {
            console.error("Error de conexión o servidor:", err);
            alert("🛑 Error crítico al enviar datos: " + err.message);
        } finally {
            btnAgendar.disabled = false;
        }
    });

    // --- Agregar al historial visualmente (Función auxiliar) ---
    function addReunionToHistorial(r) {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.innerHTML = `
            <strong>${r.fecha}</strong> - ${r.tema} <br>
            <small>${r.organizador || ""} (${r.cargo || ""})</small><br>
            Invitados: ${r.invitados || ""}<br>
            <a href="${r.link}" target="_blank">🔗 Enlace</a>
        `;
        
        // 1. Agrega el nuevo elemento al inicio (será la posición #1)
        historial.prepend(li); 
        
        // 2. Limita a un máximo de 3 elementos en la lista
        while (historial.children.length > 3) {
            // Elimina el último elemento de la lista (el más antiguo)
            historial.removeChild(historial.lastElementChild);
        }
    }
});