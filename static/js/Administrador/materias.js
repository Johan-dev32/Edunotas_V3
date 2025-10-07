// Materias por curso (601 a 1103)
const materiasBase = [
  "ESPAÑOL",
  "MATEMÁTICAS",
  "INGLÉS",
  "SOCIALES",
  "ÉTICA",
  "FILOSOFÍA",
  "EDUCACIÓN FÍSICA",
  "ARTÍSTICA",
  "BIOLÓGICA - FÍSICA - QUÍMICA",
  "RELIGIÓN",
  "TECNOLOGÍA - INFORMÁTICA",
  "P.T.I"
];

const materiasPorCurso = {};

// Generamos dinámicamente los cursos de 601 a 1103
["6", "7", "8", "9", "10", "11"].forEach(grado => {
  for (let paralelo = 1; paralelo <= 3; paralelo++) {
    let curso = grado + "0" + paralelo; // ejemplo: 601, 602, 603
    materiasPorCurso[curso] = [...materiasBase]; // clon de la lista base
  }
});

// Función para llenar materias en un <select>
function cargarMaterias(cursoId) {
  const selectMaterias = document.getElementById("materia");

  // limpiar primero
  selectMaterias.innerHTML = "";

  if (materiasPorCurso[cursoId]) {
    materiasPorCurso[cursoId].forEach(m => {
      let option = document.createElement("option");
      option.value = m.toLowerCase().replace(/\s+/g, "_");
      option.textContent = m;
      selectMaterias.appendChild(option);
    });
  }

  // Escuchar cambios para actualizar la tabla
  selectMaterias.addEventListener("change", actualizarMateriaEnTabla);

  // Mostrar por defecto la primera materia
  if (selectMaterias.options.length > 0) {
    selectMaterias.selectedIndex = 0;
    actualizarMateriaEnTabla();
  }
}

// Función que actualiza la columna "Materia" de la tabla
function actualizarMateriaEnTabla() {
  const selectMaterias = document.getElementById("materia");
  const materiaSeleccionada = selectMaterias.options[selectMaterias.selectedIndex]?.textContent;

  if (!materiaSeleccionada) return;

  // Solo tomamos las filas dentro del cuerpo (tbody)
  const filas = document.querySelectorAll("#tablaInfo tbody tr");

  filas.forEach(fila => {
    const celdaMateria = fila.cells[3]; // Columna “Materia”
    if (celdaMateria) {
      celdaMateria.textContent = materiaSeleccionada;
    }
  });
}
document.addEventListener("DOMContentLoaded", () => {
  const selectMateria = document.getElementById("materia");
  const celdasMateria = document.querySelectorAll(".celda-materia");

  if (selectMateria) {
    selectMateria.addEventListener("change", () => {
      const materiaSeleccionada = selectMateria.options[selectMateria.selectedIndex].textContent;

      celdasMateria.forEach(celda => {
        celda.textContent = materiaSeleccionada;
      });
    });
  }
});