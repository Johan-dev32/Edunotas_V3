const encuestas = [
  {
    id: 1,
    titulo: "Satisfacción con el uso de EduNotas",
    fechaCierre: "2025-11-15",
    preguntas: [
      {
        texto: "¿Cómo calificarías la plataforma EduNotas?",
        tipo: "seleccion",
        opciones: ["Excelente", "Buena", "Regular", "Mala"]
      },
      {
        texto: "¿Qué mejorarías?",
        tipo: "texto"
      }
    ],
    respondida: false
  },
  {
    id: 2,
    titulo: "Encuesta de ambiente escolar",
    fechaCierre: "2025-10-25",
    preguntas: [],
    respondida: false
  },
  {
    id: 3,
    titulo: "Opinión sobre actividades extracurriculares",
    fechaCierre: "2025-11-10",
    preguntas: [
      {
        texto: "¿Participas en actividades extracurriculares?",
        tipo: "seleccion",
        opciones: ["Sí", "No"]
      },
      {
        texto: "¿Qué tipo de actividades te gustaría tener?",
        tipo: "texto"
      }
    ],
    respondida: false
  }
];

const contenedor = document.getElementById("encuestas-container");
const modal = document.getElementById("modal");
const modalBody = document.getElementById("modal-body");
const cerrar = document.querySelector(".cerrar");

function cargarEncuestas() {
  contenedor.innerHTML = "";
  const hoy = new Date();

  encuestas.forEach(encuesta => {
    const cierre = new Date(encuesta.fechaCierre);
    const vencida = hoy > cierre;
    const estado = encuesta.respondida
      ? "Respondida"
      : vencida
      ? "Cerrada"
      : "Activa";

    const div = document.createElement("div");
    div.classList.add("encuesta");
    div.innerHTML = `
      <div class="encuesta-info">
        <h3>${encuesta.titulo}</h3>
        <p><strong>Fecha límite:</strong> ${encuesta.fechaCierre}</p>
        <p><strong>Estado:</strong> ${estado}</p>
      </div>
      <button ${encuesta.respondida || vencida ? "disabled" : ""} data-id="${encuesta.id}">
        ${encuesta.respondida ? "Respondida" : vencida ? "Cerrada" : "Responder"}
      </button>
    `;
    contenedor.appendChild(div);
  });

  document.querySelectorAll("button[data-id]").forEach(btn => {
    btn.addEventListener("click", abrirEncuesta);
  });
}

function abrirEncuesta(e) {
  const id = e.target.dataset.id;
  const encuesta = encuestas.find(enc => enc.id == id);

  modalBody.innerHTML = `
    <h2>${encuesta.titulo}</h2>
    ${encuesta.preguntas.map((p, i) => `
      <div class="pregunta">
        <p><strong>${i + 1}. ${p.texto}</strong></p>
        ${
          p.tipo === "seleccion"
            ? `<select>${p.opciones.map(o => `<option>${o}</option>`).join("")}</select>`
            : `<textarea rows="2" placeholder="Escribe tu respuesta..."></textarea>`
        }
      </div>
    `).join("")}
    <button id="enviarRespuesta">Enviar Respuesta</button>
  `;

  document.getElementById("enviarRespuesta").addEventListener("click", () => {
    encuesta.respondida = true;
    modal.style.display = "none";
    alert("Tu respuesta ha sido registrada correctamente ✅");
    cargarEncuestas();
  });

  modal.style.display = "block";
}

cerrar.addEventListener("click", () => (modal.style.display = "none"));
window.addEventListener("click", e => {
  if (e.target == modal) modal.style.display = "none";
});

cargarEncuestas();
