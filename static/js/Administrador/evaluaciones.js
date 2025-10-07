// Datos simulados de evaluaciones
const evaluaciones = [
  // Curso 901
  {
    curso: "901",
    materia: "Lengua Castellana",
    fecha: "2025-02-12",
    tipo: "Ensayo literario",
    nota: 4.5,
    comentario: "Excelente redacción y coherencia.",
    correccion: null
  },
  {
    curso: "901",
    materia: "Matemáticas",
    fecha: "2025-03-05",
    tipo: "Evaluación Trimestral",
    nota: 3.8,
    comentario: "Debe mejorar la parte de geometría.",
    correccion: null
  },
  // Curso 902
  {
    curso: "902",
    materia: "Ciencias Naturales",
    fecha: "2025-03-22",
    tipo: "Taller de laboratorio",
    nota: 4.7,
    comentario: "Excelente manejo del material.",
    correccion: null
  },
  {
    curso: "902",
    materia: "Educación Física",
    fecha: "2025-04-14",
    tipo: "Prueba de resistencia",
    nota: 4.0,
    comentario: "Buen desempeño físico general.",
    correccion: null
  },
  // Curso 1002
  {
    curso: "1002",
    materia: "Química",
    fecha: "2025-02-27",
    tipo: "Práctica de laboratorio",
    nota: 4.4,
    comentario: "Excelente en observaciones experimentales.",
    correccion: null
  },
  {
    curso: "1002",
    materia: "Matemáticas",
    fecha: "2025-03-18",
    tipo: "Examen de funciones",
    nota: 3.9,
    comentario: "Debe revisar el concepto de dominio y rango.",
    correccion: null
  },
  // Curso 1003
  {
    curso: "1003",
    materia: "Física",
    fecha: "2025-02-10",
    tipo: "Laboratorio de movimiento",
    nota: 4.2,
    comentario: "Buen trabajo con gráficas de velocidad.",
    correccion: null
  },
  {
    curso: "1003",
    materia: "Lengua Castellana",
    fecha: "2025-03-30",
    tipo: "Análisis de lectura",
    nota: 4.0,
    comentario: "Excelente interpretación textual.",
    correccion: null
  },
  // Curso 1101
  {
    curso: "1101",
    materia: "Historia",
    fecha: "2025-04-05",
    tipo: "Exposición temática",
    nota: 4.8,
    comentario: "Presentación muy clara y estructurada.",
    correccion: null
  },
  {
    curso: "1101",
    materia: "Inglés",
    fecha: "2025-04-25",
    tipo: "Reading comprehension test",
    nota: 3.6,
    comentario: "Debe reforzar comprensión de textos largos.",
    correccion: null
  }
];


// Función para buscar
document.getElementById("btnBuscar").addEventListener("click", () => {
  const curso = document.getElementById("curso").value;
  const materia = document.getElementById("materia").value;
  const tablaContainer = document.getElementById("tablaContainer");
  const titulo = document.getElementById("tituloTabla");
  const tbody = document.getElementById("tablaBody");

  // Validación
  if (!curso || !materia) {
    alert("Por favor selecciona un curso y una materia.");
    return;
  }

  // Filtrar evaluaciones
  const resultados = evaluaciones.filter(
    ev => ev.curso === curso && ev.materia === materia
  );

  // Mostrar resultados
  if (resultados.length > 0) {
    tablaContainer.style.display = "block";
    titulo.textContent = `Historial de ${materia} - Curso ${curso}`;
    tbody.innerHTML = resultados.map(ev => `
      <tr>
        <td>${ev.fecha}</td>
        <td>${ev.tipo}</td>
        <td>${ev.nota.toFixed(1)}</td>
        <td>${ev.comentario}</td>
        <td>${ev.correccion ? `
          <div class="correccion">
            <strong>Fecha:</strong> ${ev.correccion.fecha}<br>
            <strong>Motivo:</strong> ${ev.correccion.motivo}<br>
            <strong>Autorizado por:</strong> ${ev.correccion.autorizado_por}
          </div>` : "—"}
        </td>
      </tr>
    `).join('');
  } else {
    tablaContainer.style.display = "block";
    titulo.textContent = `No se encontraron evaluaciones para ${materia} en el curso ${curso}.`;
    tbody.innerHTML = "";
  }
});
