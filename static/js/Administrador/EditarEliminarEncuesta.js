document.addEventListener("DOMContentLoaded", async () => {
    const encuestasList = document.getElementById("encuestasList");
    const searchInput = document.getElementById("searchInput");
    const noEncuestasMessage = document.getElementById("noEncuestasMessage");

    let encuestas = [];
    const ADMIN_ENCUESTA_URL = "/administrador/encuestas/";

    async function cargarEncuestas() {
        try {
            const res = await fetch("/administrador/api/encuestas");
            if (!res.ok) throw new Error("Fallo al cargar encuestas");
            encuestas = await res.json();
            mostrarEncuestas(encuestas);
        } catch (err) {
            console.error("Error al cargar encuestas:", err);
            Swal.fire("Error", "No se pudieron cargar las encuestas.", "error");
        }
    }

    function mostrarEncuestas(lista) {
        encuestasList.innerHTML = "";
        if (lista.length === 0) {
            noEncuestasMessage.classList.remove("d-none");
            return;
        }
        noEncuestasMessage.classList.add("d-none");

        lista.forEach(encuesta => {
            const card = document.createElement("div");
            card.className = "card p-3";

            const resultadosBtn = `<button class="btn btn-info btn-sm" onclick="verResultados(${encuesta.id})">Resultados</button>`;
            const editarBtn = `<button class="btn btn-primary btn-sm" onclick="editarEncuesta(${encuesta.id})">Editar</button>`;
            const eliminarBtn = `<button class="btn btn-danger btn-sm" onclick="eliminarEncuesta(${encuesta.id})">Eliminar</button>`;
            const toggleBtn = `
                <form method="POST" action="${ADMIN_ENCUESTA_URL}${encuesta.id}/toggle" style="display:inline;">
                    <button type="submit" class="btn btn-secondary btn-sm">
                        ${encuesta.activa ? 'Desactivar' : 'Activar'}
                    </button>
                </form>
            `;

            card.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="titulo-encuesta" style="cursor:pointer">${encuesta.titulo} 
                        <span class="badge bg-${encuesta.activa ? 'success' : 'secondary'}">${encuesta.activa ? 'ACTIVA' : 'INACTIVA'}</span>
                    </h5>
                    <div class="btn-group">
                        ${editarBtn}
                        ${resultadosBtn}
                        ${eliminarBtn}
                        ${toggleBtn}
                    </div>
                </div>
                <div class="preguntas d-none">
                    <p><strong>Descripción:</strong> ${encuesta.descripcion || 'N/A'}</p>
                    <p><strong>Fecha de cierre:</strong> ${encuesta.fechaCierre ? new Date(encuesta.fechaCierre).toLocaleDateString() : 'N/A'}</p>
                    <p><strong>Preguntas:</strong></p>
                    <ul>
                        ${encuesta.preguntas.map(p => `<li>${p.texto} (${p.tipo})</li>`).join("")}
                    </ul>
                </div>
            `;

            card.querySelector(".titulo-encuesta").addEventListener("click", () => {
                const preguntasDiv = card.querySelector(".preguntas");
                preguntasDiv.classList.toggle("d-none");
            });

            encuestasList.appendChild(card);
        });
    }

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase();
        const filtradas = encuestas.filter(e => e.titulo.toLowerCase().includes(query));
        mostrarEncuestas(filtradas);
    });

    window.verResultados = function(id) {
        window.location.href = `${ADMIN_ENCUESTA_URL}${id}/respuestas`;
    }

    window.editarEncuesta = function(id) {
        window.location.href = `${ADMIN_ENCUESTA_URL}${id}/editar`;
    }

    window.eliminarEncuesta = async function(id) {
        const result = await Swal.fire({
            title: "¿Seguro que desea eliminar esta encuesta?",
            text: "¡Esta acción es irreversible! Solo se puede eliminar si no tiene respuestas.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            cancelButtonColor: "#6c757d",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar"
        });

        if (result.isConfirmed) {
            try {
                const res = await fetch(`${ADMIN_ENCUESTA_URL}${id}/eliminar`, { method: "DELETE" });
                const data = await res.json();
                
                if (res.ok) {
                    Swal.fire("¡Eliminada!", data.message, "success");
                    cargarEncuestas();
                } else {
                    Swal.fire("Error", data.message || "Error al eliminar la encuesta.", "error");
                }
            } catch (err) {
                console.error(err);
                Swal.fire("Error", "Ocurrió un error de conexión al eliminar.", "error");
            }
        }
    }

    cargarEncuestas();
});