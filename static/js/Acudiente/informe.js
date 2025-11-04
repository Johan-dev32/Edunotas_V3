// Datos simulados
const estudiantes = [
  {
    documento: "12345678",
    nombre: "Juan Sebastián Gómez",
    curso: "902",
    tareas: [
      {
        materia: "Matemáticas",
        tarea: "Guía de ejercicios #3",
        fecha: "10/10/2025",
        estado: "Entregada",
        nota: 4.2,
        observacion: "Cumplió con todos los puntos.",
        periodo: "2"
      },
      {
        materia: "Lengua Castellana",
        tarea: "Ensayo literario",
        fecha: "08/10/2025",
        estado: "No entregada",
        nota: "-",
        observacion: "Debe entregar en próxima fecha.",
        periodo: "2"
      },
      {
        materia: "Inglés",
        tarea: "Actividad sobre verbos irregulares",
        fecha: "12/10/2025",
        estado: "Pendiente",
        nota: "-",
        observacion: "Plazo hasta 14/10/2025.",
        periodo: "2"
      }
    ],
    observacionGeneral: "Juan ha mejorado su cumplimiento de tareas, mantener ritmo."
  }
];

const btnBuscar = document.getElementById("btnBuscar");
const documentoInput = document.getElementById("buscarDocumento");
const infoEstudiante = document.getElementById("infoEstudiante");
const nombre = document.getElementById("nombre");
const documento = document.getElementById("documento");
const curso = document.getElementById("curso");
const materiaSelect = document.getElementById("materiaSelect");
const periodoSelect = document.getElementById("periodoSelect");
const btnFiltrar = document.getElementById("btnFiltrar");
const tablaTareas = document.getElementById("tablaTareas");
const tareasBody = document.getElementById("tareasBody");
const totalTareas = document.getElementById("totalTareas");
const entregadas = document.getElementById("entregadas");
const noEntregadas = document.getElementById("noEntregadas");
const promedio = document.getElementById("promedio");
const observacionesDocente = document.getElementById("observacionesDocente");
const textoObservacion = document.getElementById("textoObservacion");

let estudianteActual = null;

// Buscar estudiante
btnBuscar.addEventListener("click", () => {
  const id = documentoInput.value.trim();
  estudianteActual = estudiantes.find(e => e.documento === id);

  if (estudianteActual) {
    infoEstudiante.classList.remove("oculto");
    nombre.textContent = estudianteActual.nombre;
    documento.textContent = estudianteActual.documento;
    curso.textContent = estudianteActual.curso;
    tablaTareas.classList.add("oculto");
    observacionesDocente.classList.add("oculto");
  } else {
    alert("No se encontró ningún estudiante con ese número de documento.");
    infoEstudiante.classList.add("oculto");
  }
});

// Filtrar tareas
btnFiltrar.addEventListener("click", () => {
  if (!estudianteActual) return;

  const materia = materiaSelect.value;
  const periodo = periodoSelect.value;

  let tareasFiltradas = estudianteActual.tareas;
  if (materia) tareasFiltradas = tareasFiltradas.filter(t => t.materia === materia);
  if (periodo) tareasFiltradas = tareasFiltradas.filter(t => t.periodo === periodo);

  if (tareasFiltradas.length === 0) {
    alert("No hay tareas registradas con esos filtros.");
    return;
  }

  tareasBody.innerHTML = "";
  let entregadasCount = 0;
  let noEntregadasCount = 0;
  let sumaNotas = 0;
  let notasValidas = 0;

  tareasFiltradas.forEach(t => {
    const fila = document.createElement("tr");
    const estadoClass =
      t.estado === "Entregada"
        ? "entregada"
        : t.estado === "No entregada"
        ? "no-entregada"
        : "pendiente";

    if (t.estado === "Entregada") entregadasCount++;
    if (t.estado === "No entregada") noEntregadasCount++;
    if (typeof t.nota === "number") {
      sumaNotas += t.nota;
      notasValidas++;
    }

    fila.innerHTML = `
      <td>${t.materia}</td>
      <td>${t.tarea}</td>
      <td>${t.fecha}</td>
      <td><span class="estado ${estadoClass}">${t.estado}</span></td>
      <td>${t.nota}</td>
      <td>${t.observacion}</td>
    `;
    tareasBody.appendChild(fila);
  });

  totalTareas.textContent = tareasFiltradas.length;
  entregadas.textContent = entregadasCount;
  noEntregadas.textContent = noEntregadasCount;
  promedio.textContent = notasValidas > 0 ? (sumaNotas / notasValidas).toFixed(2) : "-";

  tablaTareas.classList.remove("oculto");

  if (estudianteActual.observacionGeneral) {
    observacionesDocente.classList.remove("oculto");
    textoObservacion.textContent = estudianteActual.observacionGeneral;
  }
});
