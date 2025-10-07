document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formEstudiante");
  const tabla = document.querySelector("#tablaPromedios tbody");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    // Capturar valores
    const nombre = document.getElementById("nombre").value;
    const ciclo = document.getElementById("ciclo").value;
    const curso = document.getElementById("curso").value;
    const promedio = document.getElementById("promedio").value;

    // Crear fila nueva con clase especial
    const fila = document.createElement("tr");
    fila.classList.add("nuevo-registro"); // 👈 esta línea aplica el color azul

    fila.innerHTML = `
      <td>${nombre}</td>
      <td>${ciclo}</td>
      <td>${curso}</td>
      <td>${promedio}</td>
      <td>
        <a href="${urlCitacion}" class="btn btn-light btn-sm">
          <i class="bi bi-card-heading"></i>
        </a>
      </td>
    `;

    // Agregar fila a la tabla
    tabla.appendChild(fila);

    // Limpiar formulario
    form.reset();
  });
});
