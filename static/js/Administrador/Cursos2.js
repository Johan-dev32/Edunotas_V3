document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formEstudiante");
  const tabla = document.querySelector("#tablaPromedios tbody");

  // obtener la url de citaciones desde el span oculto
  const citacionesUrl = document.getElementById("citaciones-url").dataset.url;

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const nombre = document.getElementById("nombre").value;
    const ciclo = document.getElementById("ciclo").value;
    const curso = document.getElementById("curso").value;
    const promedio = document.getElementById("promedio").value;

    const fila = document.createElement("tr");

    fila.innerHTML = `
      <td>${nombre}</td>
      <td>${ciclo}</td>
      <td>${curso}</td>
      <td>${promedio}</td>
      <td>
        <a href="${citacionesUrl}" class="btn btn-light btn-sm">
          <i class="bi bi-card-heading"></i>
        </a>
      </td>
    `;

    tabla.appendChild(fila);
    form.reset();
  });
});
