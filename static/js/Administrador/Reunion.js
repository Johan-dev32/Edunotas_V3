document.addEventListener("DOMContentLoaded", () => {
  const linkBase = "https://meet.google.com/landing?hs=197&authuser=0";

  const invitadosInput = document.getElementById("invitados");
  const linkGeneradoInput = document.getElementById("linkGenerado");
  const form = document.getElementById("formReunion");
  const historial = document.getElementById("historial");

  // 🔹 Cargar historial guardado
  let reuniones = JSON.parse(localStorage.getItem("reuniones")) || [];
  renderHistorial();

  // Generar link cuando terminas de escribir invitados
  if (invitadosInput && linkGeneradoInput) {
    invitadosInput.addEventListener("blur", function () {
      const uniqueId = Date.now();
      const link = linkBase + uniqueId;
      linkGeneradoInput.value = link;
    });
  }

  // Guardar reunión
  form.addEventListener("submit", function (event) {
    event.preventDefault();

    const datos = {
      fecha: document.getElementById("fecha").value,
      tema: document.getElementById("tema").value,
      organizador: document.getElementById("organizador").value,
      cargo: document.getElementById("cargo").value,
      invitados: invitadosInput.value,
      link: linkGeneradoInput.value
    };

    if (!datos.link) {
      alert("⚠️ Primero genera el link antes de agendar.");
      return;
    }

    // 🚀 Insertar arriba y limitar a 3
    reuniones.unshift(datos); 
    reuniones = reuniones.slice(0, 3); 

    // Guardar en localStorage
    localStorage.setItem("reuniones", JSON.stringify(reuniones));

    // Mostrar en historial
    renderHistorial();

    // Abrir el link en otra pestaña
    window.open(datos.link, "_blank");

    // Limpiar formulario
    form.reset();
    linkGeneradoInput.value = "";
  });

  // Renderizar historial en la vista
  function renderHistorial() {
    historial.innerHTML = "";
    reuniones.forEach((r) => {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.innerHTML = `
        <strong>${r.fecha}</strong> - ${r.tema} <br>
        <small>${r.organizador} (${r.cargo})</small><br>
        Invitados: ${r.invitados}<br>
        <a href="${r.link}" target="_blank">🔗 Enlace</a>
      `;
      historial.appendChild(li);
    });
  }
});
