document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ informe.js cargado correctamente");

  // Verificar si Chart.js está disponible
  console.log("Chart.js disponible:", typeof Chart);

  generarTablaGrupos();
  generarTablaEstudiantes();

  // Esperar un poco por seguridad antes de generar gráficas
  setTimeout(generarGraficas, 300);

  const cicloSelect = document.getElementById("cicloSelect");
  cicloSelect.addEventListener("change", (e) => {
    const ciclo = e.target.value;
    if (ciclo) alert(`Mostrando datos del Ciclo ${ciclo}`);
  });

  document.getElementById("btnPDF").addEventListener("click", exportarPDF);
  document.getElementById("btnExcel").addEventListener("click", exportarExcel);
});

// ====================== DATOS ======================
const grupos = [
  { grado: "10°", curso: "A", director: "María Gómez", estudiantes: 28, promedio: 4.2, puesto: 3 },
  { grado: "9°", curso: "B", director: "Carlos Pérez", estudiantes: 30, promedio: 3.8, puesto: 5 },
  { grado: "11°", curso: "C", director: "Ana Rodríguez", estudiantes: 25, promedio: 4.5, puesto: 1 },
  { grado: "8°", curso: "A", director: "Sofía León", estudiantes: 32, promedio: 3.9, puesto: 6 },
  { grado: "7°", curso: "B", director: "Juan Castillo", estudiantes: 27, promedio: 4.0, puesto: 4 }
];

const estudiantes = [
  { id: "1001", nombre: "Juan Pérez", asistencias: 92, fallas: 3, retardos: 2, observaciones: 1 },
  { id: "1002", nombre: "María López", asistencias: 90, fallas: 5, retardos: 1, observaciones: 2 },
  { id: "1003", nombre: "Carlos Gómez", asistencias: 88, fallas: 6, retardos: 4, observaciones: 3 },
  { id: "1004", nombre: "Ana Torres", asistencias: 95, fallas: 2, retardos: 1, observaciones: 0 },
  { id: "1005", nombre: "Laura Díaz", asistencias: 91, fallas: 3, retardos: 3, observaciones: 2 },
  { id: "1006", nombre: "Pedro Martínez", asistencias: 87, fallas: 7, retardos: 2, observaciones: 4 },
  { id: "1007", nombre: "Camila Reyes", asistencias: 96, fallas: 1, retardos: 0, observaciones: 0 },
  { id: "1008", nombre: "Diego Castro", asistencias: 85, fallas: 10, retardos: 3, observaciones: 5 },
  { id: "1009", nombre: "Valentina Mora", asistencias: 93, fallas: 2, retardos: 2, observaciones: 1 },
  { id: "1010", nombre: "Andrés Ruiz", asistencias: 89, fallas: 5, retardos: 4, observaciones: 2 }
];

// ====================== TABLAS ======================
function generarTablaGrupos() {
  const tbody = document.querySelector("#tablaGrupo tbody");
  tbody.innerHTML = "";
  grupos.forEach(g => {
    const fila = `
      <tr>
        <td>${g.grado}</td>
        <td>${g.curso}</td>
        <td>${g.director}</td>
        <td>${g.estudiantes}</td>
        <td>${g.promedio}</td>
        <td>${g.puesto}</td>
      </tr>`;
    tbody.insertAdjacentHTML("beforeend", fila);
  });
}

function generarTablaEstudiantes() {
  const tbody = document.querySelector("#tablaEstudiantes tbody");
  tbody.innerHTML = "";
  estudiantes.forEach(e => {
    const fila = `
      <tr>
        <td>${e.id}</td>
        <td>${e.nombre}</td>
        <td>${e.asistencias}%</td>
        <td>${e.fallas}</td>
        <td>${e.retardos}</td>
        <td>${e.observaciones}</td>
      </tr>`;
    tbody.insertAdjacentHTML("beforeend", fila);
  });
}

// ====================== GRÁFICAS ======================
function generarGraficas() {
  if (typeof Chart !== "function") {
    console.error("❌ Chart.js no está disponible");
    return;
  }

  const ctx1 = document.getElementById("graficaAcademica").getContext("2d");
  new Chart(ctx1, {
    type: "bar",
    data: {
      labels: ["Matemáticas", "Ciencias", "Lengua", "Inglés", "Historia"],
      datasets: [{
        label: "Promedio del grupo",
        data: [4.2, 3.8, 4.5, 4.0, 3.9],
        backgroundColor: "#a51c30"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title: { display: true, text: "Rendimiento Académico" }
      }
    }
  });

  const ctx2 = document.getElementById("graficaAsistencia").getContext("2d");
  new Chart(ctx2, {
    type: "doughnut",
    data: {
      labels: ["Asistencias", "Fallas", "Retardos"],
      datasets: [{
        data: [85, 10, 5],
        backgroundColor: ["#28a745", "#dc3545", "#ffc107"]
      }]
    },
    options: {
      plugins: {
        title: { display: true, text: "Asistencia del Grupo" }
      }
    }
  });

  const ctx3 = document.getElementById("graficaConducta").getContext("2d");
  new Chart(ctx3, {
    type: "line",
    data: {
      labels: ["Ciclo 1", "Ciclo 2", "Ciclo 3"],
      datasets: [{
        label: "Conducta",
        data: [4.5, 4.2, 4.6],
        borderColor: "#a51c30",
        tension: 0.3
      }]
    },
    options: {
      plugins: {
        title: { display: true, text: "Evolución Disciplinaria" }
      },
      scales: { y: { min: 0, max: 5 } }
    }
  });

  console.log("✅ Gráficas generadas correctamente");
}

// ====================== EXPORTAR ======================
async function exportarPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF("p", "mm", "a4");
  const elemento = document.querySelector(".container");

  const canvas = await html2canvas(elemento, { scale: 2 });
  const imgData = canvas.toDataURL("image/png");

  const imgProps = doc.getImageProperties(imgData);
  const pdfWidth = doc.internal.pageSize.getWidth();
  const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

  doc.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
  doc.save("informe_desempeno.pdf");
}

function exportarExcel() {
  const tabla = document.getElementById("tablaEstudiantes");
  const html = tabla.outerHTML.replace(/ /g, "%20");
  const a = document.createElement("a");
  a.href = "data:application/vnd.ms-excel," + html;
  a.download = "reporte_estudiantes.xls";
  a.click();
}
