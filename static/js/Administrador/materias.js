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
}
