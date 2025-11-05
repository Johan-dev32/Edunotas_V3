document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formReunion");
  const fechaInput = document.getElementById("fecha");
  const temaInput = document.getElementById("tema");
  const organizadorInput = document.getElementById("organizador");
  const cargoInput = document.getElementById("cargo");
  const invitadosInput = document.getElementById("invitados");
  const linkGeneradoInput = document.getElementById("linkGenerado");
  const historial = document.getElementById("historial");

  const linkBase = "https://meet.google.com/landing?hs=197&authuser=0";

  // Cargar historial desde servidor
  fetch("/admin/reuniones/historial")
    .then(res => res.json())
    .then(data => data.forEach(addReunionToHistorial));

  // Generar link cuando se sale del input de invitados
  invitadosInput.addEventListener("blur", () => {
    const uniqueId = Date.now();
    linkGeneradoInput.value = linkBase + uniqueId;
  });

  // Interceptar submit
  form.addEventListener("submit", e => {
    e.preventDefault();

    if (!linkGeneradoInput.value) {
      alert("⚠️ Primero genera el link antes de agendar.");
      return;
    }

    const datos = {
      fecha: fechaInput.value,
      tema: temaInput.value,
      organizador: organizadorInput.value,
      cargo: cargoInput.value,
      invitados: invitadosInput.value,
      link: linkGeneradoInput.value
    };

    // Enviar al servidor
    fetch("/admin/reuniones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos)
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        addReunionToHistorial(datos);
        form.reset();
        linkGeneradoInput.value = "";
        window.open(datos.link, "_blank");
      } else {
        alert("Error al guardar en el servidor: " + (data.error || "Desconocido"));
      }
    })
    .catch(err => alert("Error de conexión: " + err));
  });

  function addReunionToHistorial(r) {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.innerHTML = `
      <strong>${r.fecha}</strong> - ${r.tema} <br>
      <small>${r.organizador} (${r.cargo})</small><br>
      Invitados: ${r.invitados}<br>
      <a href="${r.link}" target="_blank">🔗 Enlace</a>
    `;
    historial.prepend(li);
  }
});
