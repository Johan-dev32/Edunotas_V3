document.addEventListener("DOMContentLoaded", () => {
  const linkBase = "https://meet.google.com/landing?hs=197&authuser=0";

  const invitadosInput = document.getElementById("invitados");
  const linkGeneradoInput = document.getElementById("linkGenerado");
  const btnAgendar = document.getElementById("btnAgendar");

  // Generar link cuando terminas de escribir invitados
  if (invitadosInput && linkGeneradoInput) {
    invitadosInput.addEventListener("blur", function () {
      const uniqueId = Date.now();
      const link = linkBase + uniqueId;
      linkGeneradoInput.value = link;
    });
  }

  // Redirigir al link al hacer clic en Agendar Reunión
  if (btnAgendar && linkGeneradoInput) {
    btnAgendar.addEventListener("click", function (event) {
      event.preventDefault(); // evita que el form recargue la página

      const link = linkGeneradoInput.value;
      if (link) {
        window.open(link, "_blank"); // abre en nueva pestaña
        // window.location.href = link; // si lo quieres en la misma pestaña
      } else {
        alert("Primero debes generar el link de la reunión.");
      }
    });
  }
});