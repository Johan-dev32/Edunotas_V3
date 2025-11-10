document.addEventListener("DOMContentLoaded", async () => {
    const encuestasList = document.getElementById("encuestasList");
    const searchInput = document.getElementById("searchInput");
    const noEncuestasMessage = document.getElementById("noEncuestasMessage");

    let encuestas = [];

    // Cargar encuestas desde el backend
    async function cargarEncuestas() {
        try {
            const res = await fetch("/administrador/api/encuestas");
            encuestas = await res.json();
            mostrarEncuestas(encuestas);
        } catch (err) {
            console.error(err);
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

            card.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="titulo-encuesta" style="cursor:pointer">${encuesta.titulo}</h5>
                    <div class="btn-group">
                        <button class="btn btn-primary btn-sm" onclick="editarEncuesta(${encuesta.id})">Editar</button>
                        <button class="btn btn-danger btn-sm" onclick="eliminarEncuesta(${encuesta.id})">Eliminar</button>
                        <button class="btn btn-secondary btn-sm" onclick="toggleEncuesta(${encuesta.id})">
                            ${encuesta.activa ? 'Desactivar' : 'Activar'}
                        </button>
                    </div>
                </div>
                <div class="preguntas d-none">
                    <p><strong>Descripción:</strong> ${encuesta.descripcion || ''}</p>
                    <p><strong>Fecha de cierre:</strong> ${encuesta.fechaCierre || ''}</p>
                    <p><strong>Preguntas:</strong></p>
                    <ul>
                        ${encuesta.preguntas.map(p => `<li>${p.texto} (${p.tipo})</li>`).join("")}
                    </ul>
                </div>
            `;

            // Toggle para mostrar/ocultar preguntas
            card.querySelector(".titulo-encuesta").addEventListener("click", () => {
                const preguntasDiv = card.querySelector(".preguntas");
                preguntasDiv.classList.toggle("d-none");
            });

            encuestasList.appendChild(card);
        });
    }

    // Filtrar encuestas por título
    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase();
        const filtradas = encuestas.filter(e => e.titulo.toLowerCase().includes(query));
        mostrarEncuestas(filtradas);
    });

    // Funciones globales
    window.editarEncuesta = function(id) {
        window.location.href = `/administrador/encuestas/${id}/editar`;
    }

    window.eliminarEncuesta = async function(id) {
        if (!confirm("¿Seguro que desea eliminar esta encuesta?")) return;
        try {
            const res = await fetch(`/administrador/encuestas/${id}/eliminar`, { method: "DELETE" });
            if (res.ok) {
                alert("Encuesta eliminada correctamente.");
                cargarEncuestas();
            } else {
                alert("Error al eliminar la encuesta.");
            }
        } catch (err) {
            console.error(err);
        }
    }

    window.toggleEncuesta = async function(id) {
        try {
            const res = await fetch(`/administrador/encuestas/${id}/toggle`, { method: "POST" });
            if (res.ok) {
                cargarEncuestas();
            } else {
                alert("Error al actualizar el estado de la encuesta.");
            }
        } catch (err) {
            console.error(err);
        }
    }

    // Inicializa la lista
    cargarEncuestas();
});