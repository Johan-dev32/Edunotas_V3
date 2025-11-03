const detalles = {
  1: {
    comentario: "Buen desempeño, revisar temas de álgebra avanzada.",
    modificacion: {
      huboCambio: true,
      descripcion: "Corrección de nota por revisión.",
      fecha: "12/10/2025",
      autorizadoPor: "Coordinador Académico"
    }
  },
  2: {
    comentario: "Participación activa, pero faltó completar el último ejercicio.",
    modificacion: { huboCambio: false }
  },
  3: {
    comentario: "Mejoró su redacción, excelente progreso.",
    modificacion: {
      huboCambio: true,
      descripcion: "Ajuste en la nota por reevaluación de contenido.",
      fecha: "25/08/2025",
      autorizadoPor: "Director de Grupo"
    }
  }
};

const modal = document.getElementById("modal");
const modalBody = document.getElementById("modal-body");
const cerrar = document.querySelector(".cerrar");

document.querySelectorAll(".ver-detalle").forEach(boton => {
  boton.addEventListener("click", () => {
    const id = boton.dataset.id;
    const data = detalles[id];
    modalBody.innerHTML = `
      <h2>Detalles de la Evaluación</h2>
      <p><strong>Comentario del profesor:</strong> ${data.comentario}</p>
      ${data.modificacion.huboCambio ? `
        <div class="modificacion">
          <h3>Registro de Modificación</h3>
          <p><strong>Descripción:</strong> ${data.modificacion.descripcion}</p>
          <p><strong>Fecha:</strong> ${data.modificacion.fecha}</p>
          <p><strong>Autorizado por:</strong> ${data.modificacion.autorizadoPor}</p>
        </div>
      ` : `<p><em>No se registran modificaciones.</em></p>`}
    `;
    modal.style.display = "block";
  });
});

cerrar.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target == modal) modal.style.display = "none";
});

