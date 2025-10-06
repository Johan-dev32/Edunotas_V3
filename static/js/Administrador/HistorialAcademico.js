document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector(".custom-input");
  const btnBuscar = document.getElementById("btnBuscar");

  btnBuscar.addEventListener("click", (e) => {
    e.preventDefault();

    const documento = input.value.trim();
    const destino = btnBuscar.dataset.url; // ✅ toma la URL del HTML

    if (documento === "") {
      alert("Por favor ingrese un número de documento.");
      return;
    }

    if (documento === "1016950313") {
      window.location.href = destino; // ✅ redirecciona correctamente
    } else {
      alert("Número de documento no encontrado.");
    }
  });
});
