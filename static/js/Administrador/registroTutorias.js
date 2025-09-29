// registroTutorias.js

// Guardar los datos del formulario en localStorage
function guardarTutoria() {
  const tutoria = {
    nombre: document.getElementById("nombre").value,
    rol: document.getElementById("rol").value,
    tema: document.getElementById("Tema").value,
    fecha: document.getElementById("fecha").value,
    curso: document.querySelector("select.form-select").value,
    estudiante: document.getElementById("nombre_estudiante").value,
    correo: document.getElementById("correo").value,
    motivo: document.getElementById("motivo").value,
    observaciones: document.getElementById("observaciones").value 
  };

  let tutorias = JSON.parse(localStorage.getItem("tutorias")) || [];
  tutorias.push(tutoria);
  localStorage.setItem("tutorias", JSON.stringify(tutorias));

  // Redirigir a la tabla
  window.location.href = "/registrotutorias"; // ajusta según tu ruta Flask
}

// Mostrar los datos guardados en la tabla
function mostrarTutorias() {
  const tabla = document.querySelector(".tabla-tutorias");
  const accionesDiv = document.getElementById("accionesTutorias");

  if (!tabla) return;

  let tutorias = JSON.parse(localStorage.getItem("tutorias")) || [];

  // limpiar tabla (menos cabecera) y botones
  tabla.querySelectorAll("tr:not(:first-child)").forEach(tr => tr.remove());
  accionesDiv.innerHTML = "";

  tutorias.forEach((t, index) => {
    // fila con datos
    let fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${t.nombre}</td>
      <td>${t.rol}</td>
      <td>${t.tema}</td>
      <td>${t.fecha}</td>
      <td>${t.curso}</td>
      <td>${t.estudiante}</td>
      <td>${t.correo}</td>
      <td>${t.motivo}</td>
      <td>${t.observaciones}</td>
      
    `;
    tabla.appendChild(fila);

    // botón eliminar afuera
    let boton = document.createElement("button");
    boton.className = "btn btn-danger btn-sm mb-1";
    boton.innerHTML = `<i class="bi bi-trash3-fill"></i>`;
    boton.addEventListener("click", () => {
      tutorias.splice(index, 1);
      localStorage.setItem("tutorias", JSON.stringify(tutorias));
      mostrarTutorias();
    });

    accionesDiv.appendChild(boton);
  });

}
// Llamar a mostrarTutorias cuando cargue registrotutorias.html
document.addEventListener("DOMContentLoaded", mostrarTutorias);
