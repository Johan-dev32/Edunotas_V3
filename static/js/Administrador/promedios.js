let filaSeleccionada = null;

const estudiantes = [
  { nombre: "Laura Gómez", documento: "1029384756", tipo: "CC", promedio: 4.7, observacion: "Excelente", periodo: "2025-1" },
  { nombre: "Carlos Pérez", documento: "1122334455", tipo: "CC", promedio: 3.5, observacion: "Cumple", periodo: "2025-1" },
  { nombre: "Ana Torres", documento: "9988776655", tipo: "TI", promedio: 2.8, observacion: "Debe mejorar", periodo: "2025-1" },
];

function getNivelDesempeno(promedio) {
  if (promedio >= 4.5) return { texto: "Alto", clase: "alto" };
  if (promedio >= 3.0) return { texto: "Medio", clase: "medio" };
  return { texto: "Bajo", clase: "bajo" };
}

function renderTabla(listaEstudiantes = estudiantes) {
  const tbody = document.querySelector("#tablaPromedios tbody");
  tbody.innerHTML = "";

  listaEstudiantes.forEach((est, index) => {
    const nivel = getNivelDesempeno(est.promedio);
    const fila = document.createElement("tr");

    fila.innerHTML = `
      <td>${est.nombre}</td>
      <td>${est.documento}</td>
      <td>${est.tipo}</td>
      <td>${est.promedio.toFixed(2)}</td>
      <td><span class="bolita ${nivel.clase}"></span>${nivel.texto}</td>
      <td>${est.observacion}</td>
      <td>${est.periodo}</td>
    `;

    fila.addEventListener("click", () => {
      if (filaSeleccionada) filaSeleccionada.classList.remove("fila-seleccionada");
      filaSeleccionada = fila;
      filaSeleccionada.classList.add("fila-seleccionada");
      document.getElementById("contenedorObservacion").classList.remove("d-none");
    });

    tbody.appendChild(fila);
  });
}

// Barra de búsqueda
document.getElementById("busqueda").addEventListener("input", (e) => {
  const filtro = e.target.value.toLowerCase();
  const filtrados = estudiantes.filter(est =>
    est.nombre.toLowerCase().includes(filtro) || est.documento.includes(filtro)
  );
  renderTabla(filtrados);
});

// Exportar PDF
document.getElementById("btnPdf").addEventListener("click", () => {
  const element = document.querySelector(".tabla-container");
  html2pdf().from(element).save("promedios.pdf");
});

// Enviar WhatsApp
document.getElementById("btnWhatsApp").addEventListener("click", () => {
  alert("Se enviará el reporte general por WhatsApp a los acudientes.");
});

// Agregar observación
document.getElementById("btnAgregarObservacion").addEventListener("click", () => {
  const input = document.getElementById("nuevaObservacion");
  const valor = input.value.trim();
  if (!filaSeleccionada) return alert("Selecciona una fila primero");
  if (valor === "") return alert("Escribe una observación");

  const index = Array.from(filaSeleccionada.parentNode.children).indexOf(filaSeleccionada);
  estudiantes[index].observacion = valor;

  renderTabla();
  input.value = "";
  filaSeleccionada = null;
  document.getElementById("contenedorObservacion").classList.add("d-none");
});

// Inicializar tabla
renderTabla();
