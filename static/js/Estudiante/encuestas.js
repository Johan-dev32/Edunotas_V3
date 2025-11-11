document.addEventListener("DOMContentLoaded", async () => {
    const contenedor = document.getElementById("encuestas-container");
    // Inicialización del modal de Bootstrap
    const modalElement = document.getElementById('encuestaModal');
    const modalBootstrap = new bootstrap.Modal(modalElement); 
    const modalBody = document.getElementById("modal-body-bs");
    const modalTitle = document.getElementById("encuestaModalLabel");
    let encuestaSeleccionada = null;

    // ✅ Cargar encuestas activas
    async function cargarEncuestas() {
        try {
            const res = await fetch("/estudiante/api/encuestas");
            console.log("Respuesta fetch:", res);
            if (!res.ok) throw new Error("Error al cargar encuestas");
            const encuestas = await res.json();

            console.log("✅ DATOS RECIBIDOS EN JS:", encuestas);
            
            contenedor.innerHTML = "";

            if (encuestas.length === 0) {
                contenedor.innerHTML = `<div class="alert alert-info text-center">No hay encuestas disponibles.</div>`;
                return;
            }

            encuestas.forEach((encuesta) => {
                const card = document.createElement("div");
                card.className = "card mb-3 shadow-sm";

                // Mostrar estado
                let estado = "";
                if (encuesta.vencida) {
                    estado = `<span class="badge bg-secondary">Vencida</span>`;
                } else if (encuesta.respondida) {
                    estado = `<span class="badge bg-success">Respondida</span>`;
                } else {
                    estado = `<span class="badge bg-primary">Activa</span>`;
                }

                // Botón “Responder”
                const boton = !encuesta.vencida && !encuesta.respondida
                    ? `<button class="btn btn-primary btn-responder" data-id="${encuesta.id}">Responder</button>`
                    : "";

                card.innerHTML = `
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="card-title mb-1">${encuesta.titulo}</h5>
                            <p class="mb-1 text-muted small">${encuesta.descripcion || ""}</p>
                            <p class="mb-0 text-muted small"><strong>Cierra:</strong> ${encuesta.fechaCierre}</p>
                        </div>
                        <div class="text-end">
                            ${estado}<br>
                            ${boton}
                        </div>
                    </div>
                `;
                contenedor.appendChild(card);
            });

            // Asignar eventos a botones de forma dinámica
            document.querySelectorAll(".btn-responder").forEach((btn) => {
                btn.addEventListener("click", (e) => {
                    const id = e.target.getAttribute("data-id");
                    abrirModal(id);
                });
            });

        } catch (error) {
            console.error("Error al cargar encuestas:", error);
            contenedor.innerHTML = `<div class="alert alert-danger text-center">Error al cargar encuestas.</div>`;
        }
    }

    // ✅ Abrir modal con preguntas
    async function abrirModal(idEncuesta) {
        try {
            const res = await fetch(`/estudiante/api/encuestas/${idEncuesta}`);
            if (!res.ok) throw new Error("Error al cargar preguntas");

            encuestaSeleccionada = await res.json();
            
            modalTitle.textContent = encuestaSeleccionada.titulo;

            // Construye el cuerpo del formulario
            let formHTML = '';
            encuestaSeleccionada.preguntas.forEach((p) => {
                const tipoRespuesta = p.tipo ? p.tipo.toLowerCase() : 'texto';
                let input = "";
                
                // Construcción de inputs/selects con validación 'required'
                if (tipoRespuesta === "texto" || tipoRespuesta === "opcionsimple") {
                    input = `<input type="text" class="form-control" name="preg_${p.ID_Pregunta}" placeholder="Tu respuesta..." required>`;
                } else if (tipoRespuesta === "seleccion" && p.opciones && p.opciones.length > 0) {
                    input = `
                        <select class="form-select" name="preg_${p.ID_Pregunta}" required>
                            <option value="">Selecciona una opción</option>
                            ${p.opciones.map(o => `<option value="${o.trim()}">${o.trim()}</option>`).join("")}
                        </select>
                    `;
                } else if (tipoRespuesta === "textarea") { 
                    input = `<textarea class="form-control" name="preg_${p.ID_Pregunta}" rows="3" placeholder="Tu respuesta..." required></textarea>`;
                } else {
                    input = `<input type="text" class="form-control" name="preg_${p.ID_Pregunta}" placeholder="Tu respuesta..." required>`;
                }

                formHTML += `
                    <div class="mb-3">
                        <label class="form-label"><strong>${p.texto}</strong></label>
                        ${input}
                    </div>
                `;
            });


            modalBody.innerHTML = `
                <p>${encuestaSeleccionada.descripcion || ""}</p>
                <hr>
                <form id="formEncuesta">
                    ${formHTML}
                    <div class="text-end mt-3">
                        <button type="submit" class="btn btn-primary">Enviar respuestas</button>
                    </div>
                </form>
            `;

            const form = modalBody.querySelector("#formEncuesta");
            form.addEventListener("submit", enviarRespuestas);

            modalBootstrap.show(); 
            
        } catch (err) {
            console.error(err);
            alert("Error al cargar la encuesta.");
        }
    }

    // ✅ Enviar respuestas
    async function enviarRespuestas(e) {
        e.preventDefault();
        
        // Validación de formulario
        if (!e.target.checkValidity()) {
            e.stopPropagation();
            alert("Por favor, completa todas las preguntas requeridas.");
            return;
        }

        if (!encuestaSeleccionada) return;

        const formData = new FormData(e.target);
        const respuestas = {};
        
        // Recolección y limpieza de respuestas
        encuestaSeleccionada.preguntas.forEach((p) => {
            const respuesta = formData.get(`preg_${p.ID_Pregunta}`);
            if (respuesta && respuesta.trim()) {
                respuestas[p.ID_Pregunta] = respuesta.trim();
            }
        });
        
        if (Object.keys(respuestas).length === 0) {
            alert("Debes responder al menos una pregunta para enviar la encuesta.");
            return;
        }

        try {
            const btnEnviar = e.submitter;
            btnEnviar.disabled = true;
            btnEnviar.textContent = "Enviando...";

            const res = await fetch(`/estudiante/api/encuestas/${encuestaSeleccionada.id}/responder`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ respuestas }),
            });

            btnEnviar.disabled = false;
            btnEnviar.textContent = "Enviar respuestas";

            if (res.ok) {
                alert("✅ Encuesta respondida correctamente");
                modalBootstrap.hide();
                cargarEncuestas(); 
            } else {
                const errorData = await res.json();
                alert(`❌ Error al enviar respuestas: ${errorData.error || 'Intenta de nuevo.'}`);
            }
        } catch (err) {
            console.error(err);
            alert("Error de conexión");
            e.submitter.disabled = false;
            e.submitter.textContent = "Enviar respuestas";
        }
    }

    // Inicializar la carga al inicio
    cargarEncuestas();
});