// Referencias a elementos reales en tu HTML
const btnAbrirFormulario = document.getElementById("btnAbrirFormulario");
const modalFormulario = document.getElementById("modalFormulario");
const btnCancelar = document.getElementById("btnCancelar");
const formObservacion = document.getElementById("formObservacion");
const tablaObservador = document.querySelector("#tablaObservador");
const seccionObservador = document.getElementById("observador");

// Mostrar el formulario modal
btnAbrirFormulario.addEventListener("click", () => {
  modalFormulario.classList.remove("oculto");
});

// Ocultar el formulario al hacer clic en "Cancelar"
btnCancelar.addEventListener("click", () => {
  modalFormulario.classList.add("oculto");
});

// Manejar envío del formulario
formObservacion.addEventListener("submit", (e) => {
  e.preventDefault();

  // Obtener valores de los campos
  const nombre = document.getElementById("nombre").value;
  const comportamiento = document.getElementById("comportamiento").value;
  const actitud = document.getElementById("actitud").value;
  const avances = document.getElementById("avances").value;
  const dificultades = document.getElementById("dificultades").value;
  const seguimiento = document.getElementById("seguimiento").value;

  // Crear nueva fila con los datos
  const fila = document.createElement("tr");
  fila.innerHTML = `
    <td>${nombre}</td>
    <td>${comportamiento}</td>
    <td>${actitud}</td>
    <td>${avances}</td>
    <td>${dificultades}</td>
    <td>${seguimiento}</td>
  `;

  // Agregar fila a la tabla
  tablaObservador.appendChild(fila);

  // Mostrar sección del observador si está oculta
  seccionObservador.classList.remove("oculto");

  // Limpiar y cerrar formulario
  formObservacion.reset();
  modalFormulario.classList.add("oculto");
});