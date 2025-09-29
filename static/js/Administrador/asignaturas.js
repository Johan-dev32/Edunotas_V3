let asignaturas = [];
let editIndex = null;
let selectedIndex = null;

// Diccionario de ciclos y sus cursos
const ciclos = {
  "1": ["601", "602", "603", "701", "702", "703"],
  "2": ["801", "802", "803", "901", "902", "903"],
  "3": ["1001", "1002", "1003", "1101", "1102", "1103"]
};

function mostrarFormulario(index = null) {
  document.getElementById("modal").style.display = "flex";
  document.getElementById("tituloForm").innerText = index !== null ? "Editar Asignatura" : "Agregar Asignatura";
  editIndex = index;

  if (index !== null) {
    let a = asignaturas[index];
    document.getElementById("nombreAsignatura").value = a.nombre;
    document.getElementById("descripcionAsignatura").value = a.descripcion;
    document.getElementById("cicloAsignatura").value = a.ciclo;
    document.getElementById("profesorAsignatura").value = a.profesor;
  } else {
    document.getElementById("nombreAsignatura").value = "";
    document.getElementById("descripcionAsignatura").value = "";
    document.getElementById("cicloAsignatura").value = "";
    document.getElementById("profesorAsignatura").value = "";
  }
}

function cerrarModal() {
  document.getElementById("modal").style.display = "none";
  editIndex = null;
}

function guardarAsignatura() {
  let nombre = document.getElementById("nombreAsignatura").value;
  let descripcion = document.getElementById("descripcionAsignatura").value;
  let ciclo = document.getElementById("cicloAsignatura").value;
  let profesor = document.getElementById("profesorAsignatura").value;

  if (!nombre || !ciclo || !profesor) {
    alert("El nombre, ciclo y profesor son obligatorios");
    return;
  }

  let cursos = ciclos[ciclo];

  let nueva = { nombre, descripcion, ciclo, cursos, profesor, activa: true };

  if (editIndex !== null) {
    asignaturas[editIndex] = nueva;
  } else {
    asignaturas.push(nueva);
  }

  renderTabla();
  cerrarModal();
}

function renderTabla() {
  let tbody = document.querySelector("#tablaAsignaturas tbody");
  tbody.innerHTML = "";
  asignaturas.forEach((a, i) => {
    let tr = document.createElement("tr");
    tr.className = a.activa ? "" : "inactive";
    if (i === selectedIndex) tr.classList.add("selected");
    tr.onclick = () => seleccionarFila(i);
    tr.innerHTML = `
      <td>${a.nombre}</td>
      <td>${a.descripcion}</td>
      <td>Ciclo ${a.ciclo}</td>
      <td>${a.cursos.join(", ")}</td>
      <td>${a.profesor}</td>
      <td>${a.activa ? "Activa" : "Inactiva"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function seleccionarFila(index) {
  selectedIndex = index;
  renderTabla();
}

function editarAsignatura() {
  if (selectedIndex === null) {
    alert("Seleccione una asignatura de la tabla");
    return;
  }
  mostrarFormulario(selectedIndex);
}

function desactivarAsignatura() {
  if (selectedIndex === null) {
    alert("Seleccione una asignatura de la tabla");
    return;
  }
  asignaturas[selectedIndex].activa = false;
  renderTabla();
}

// Cerrar modal al hacer clic afuera
window.onclick = function(e) {
  if (e.target.id === "modal") {
    cerrarModal();
  }
}
