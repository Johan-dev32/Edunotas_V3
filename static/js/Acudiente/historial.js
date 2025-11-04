// Datos simulados
const estudiantes = [
  {
    documento: "1145224616",
    nombre: "Juan Sebastián Gómez",
    grado: "9°",
    curso: "902",
    periodos: {
      1: {
        materias: [
          { nombre: "Matemáticas", notas: [4.0, 3.8, 4.2], final: 4.0 },
          { nombre: "Lengua Castellana", notas: [4.3, 4.0, 4.5], final: 4.3 },
          { nombre: "Ciencias Naturales", notas: [3.8, 4.0, 3.9], final: 3.9 }
        ],
        resultado: "APROBADO",
        recuperaciones: [],
        observaciones: "Buen rendimiento académico."
      },
      2: {
        materias: [
          { nombre: "Matemáticas", notas: [3.5, 3.6, 3.9], final: 3.7 },
          { nombre: "Lengua Castellana", notas: [4.0, 4.2, 4.4], final: 4.2 },
          { nombre: "Ciencias Naturales", notas: [3.2, 3.5, 3.7], final: 3.5 }
        ],
        resultado: "APROBADO CON OBSERVACIÓN",
        recuperaciones: [
          { materia: "Ciencias Naturales", nota: 3.8 }
        ],
        observaciones: "Debe reforzar Ciencias Naturales."
      }
    }
  }
];

const btnBuscar = document.getElementById("btnBuscar");
const documentoInput = document.getElementById("buscarDocumento");
const infoEstudiante = document.getElementById("infoEstudiante");
const nombre = document.getElementById("nombre");
const documento = document.getElementById("documento");
const grado = document.getElementById("grado");
const curso = document.getElementById("curso");
const periodoSelect = document.getElementById("periodoSelect");
const tablaNotas = document.getElementById("tablaNotas");
const notasBody = document.getElementById("notasBody");
const resultadoFinal = document.getElementById("resultadoFinal");
const recuperaciones = document.getElementById("recuperaciones");
const listaRecuperaciones = document.getElementById("listaRecuperaciones");
const observaciones = document.getElementById("observaciones");
const textoObservaciones = document.getElementById("textoObservaciones");

let estudianteActual = null;

// Buscar estudiante
btnBuscar.addEventListener("click", () => {
  const id = documentoInput.value.trim();
  estudianteActual = estudiantes.find(e => e.documento === id);

  if (estudianteActual) {
    infoEstudiante.classList.remove("oculto");
    nombre.textContent = estudianteActual.nombre;
    documento.textContent = estudianteActual.documento;
    grado.textContent = estudianteActual.grado;
    curso.textContent = estudianteActual.curso;
    tablaNotas.classList.add("oculto");
    periodoSelect.value = "";
  } else {
    alert("No se encontró ningún estudiante con ese número de documento.");
    infoEstudiante.classList.add("oculto");
  }
});

// Mostrar notas según período
periodoSelect.addEventListener("change", () => {
  const periodo = periodoSelect.value;
  if (!periodo || !estudianteActual) return;

  const dataPeriodo = estudianteActual.periodos[periodo];
  if (!dataPeriodo) {
    alert("No hay información registrada para este período.");
    return;
  }

  notasBody.innerHTML = "";
  dataPeriodo.materias.forEach(m => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${m.nombre}</td>
      <td>${m.notas[0]}</td>
      <td>${m.notas[1]}</td>
      <td>${m.notas[2]}</td>
      <td>${m.final}</td>
    `;
    notasBody.appendChild(fila);
  });

  resultadoFinal.textContent = dataPeriodo.resultado;
  tablaNotas.classList.remove("oculto");

  // Recuperaciones
  if (dataPeriodo.recuperaciones.length > 0) {
    recuperaciones.classList.remove("oculto");
    listaRecuperaciones.innerHTML = "";
    dataPeriodo.recuperaciones.forEach(r => {
      const li = document.createElement("li");
      li.textContent = `${r.materia}: nota ${r.nota}`;
      listaRecuperaciones.appendChild(li);
    });
  } else {
    recuperaciones.classList.add("oculto");
  }

  // Observaciones
  if (dataPeriodo.observaciones) {
    observaciones.classList.remove("oculto");
    textoObservaciones.textContent = dataPeriodo.observaciones;
  } else {
    observaciones.classList.add("oculto");
  }
});
