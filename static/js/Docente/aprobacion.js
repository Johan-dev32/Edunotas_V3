// Datos de ejemplo
const students = [
  { documento: "1234567", nombre: "Juan Pérez", asignatura: "Matemáticas 802", nota: 4.6, profesor: "Profe Laura", periodo: "2025-1", observacion: "" },
  { documento: "7654321", nombre: "Ana Gómez", asignatura: "Matemáticas 802", nota: 3.2, profesor: "Profe Laura", periodo: "2025-1", observacion: "" },
  { documento: "9876543", nombre: "Carlos Díaz", asignatura: "Matemáticas 802", nota: 2.8, profesor: "Profe Laura", periodo: "2025-1", observacion: "" }
];

const table = document.getElementById("studentTable");
const searchInput = document.getElementById("searchInput");

function getEstado(nota){
  return nota >= 3.0 ? "Aprobado" : "Reprobado";
}

function getNivel(nota){
  if(nota >= 4.5) return "Alto";
  if(nota >= 3.0) return "Medio";
  return "Bajo";
}

function renderTable(data){
  table.innerHTML = "";
  data.forEach((s, index) => {
    const estado = getEstado(s.nota);
    const nivel = getNivel(s.nota);

    table.innerHTML += `
      <tr>
        <td>${s.documento}</td>
        <td>${s.nombre}</td>
        <td>${s.asignatura}</td>
        <td>${s.nota.toFixed(1)}</td>
        <td class="${estado === 'Aprobado' ? 'status-aprobado' : 'status-reprobado'}">${estado}</td>
        <td class="nivel-${nivel.toLowerCase()}">${nivel}</td>
        <td>${s.profesor}</td>
        <td>${s.periodo}</td>
        <td>${s.observacion || '—'}</td>
        <td><button onclick="openModal(${index})">Agregar</button></td>
      </tr>`;
  });
}

searchInput.addEventListener("input", () => {
  const value = searchInput.value.toLowerCase();
  const filtered = students.filter(s => s.documento.includes(value));
  renderTable(filtered);
});

renderTable(students);

// Modal
const modal = document.getElementById("modal");
const modalName = document.getElementById("modalName");
const modalCourse = document.getElementById("modalCourse");
const modalDate = document.getElementById("modalDate");
const modalObservation = document.getElementById("modalObservation");
let currentIndex = null;

function openModal(index){
  currentIndex = index;
  modalName.value = students[index].nombre;
  modalCourse.value = students[index].asignatura;
  modal.classList.remove("hidden");
}

document.getElementById("closeModal").addEventListener("click", () => {
  modal.classList.add("hidden");
});

document.getElementById("saveObservation").addEventListener("click", () => {
  students[currentIndex].observacion = modalObservation.value;
  renderTable(students);
  modal.classList.add("hidden");
});