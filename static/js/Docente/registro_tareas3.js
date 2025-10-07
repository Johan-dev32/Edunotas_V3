document.addEventListener("DOMContentLoaded", () => {
  const inputPDF = document.getElementById("pdfUpload");
  const fileInfo = document.getElementById("fileInfo");
  const subirArchivoBtn = document.getElementById("subirArchivoBtn");
  const cancelarEntregaBtn = document.getElementById("cancelarEntregaBtn");
  const actividadTexto = document.getElementById("actividadTexto");

  // Mostrar nombre del archivo PDF seleccionado
  inputPDF.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) {
      fileInfo.innerHTML = `<p class="text-success fw-bold">Archivo seleccionado: ${file.name}</p>`;
    }
  });

  // Confirmar entrega
  subirArchivoBtn.addEventListener("click", () => {
    if (!inputPDF.files.length) {
      alert("Primero selecciona un archivo PDF antes de subirlo.");
      return;
    }

    const confirmar = confirm("¿Seguro que quieres subir este archivo?");
    if (confirmar) {
      actividadTexto.innerHTML = "<h1 class='entregado-texto'>ENTREGADO</h1>";
      subirArchivoBtn.classList.add("disabled");
      subirArchivoBtn.textContent = "Archivo Subido";
      cancelarEntregaBtn.classList.remove("d-none"); // Mostrar botón cancelar
    }
  });

  // Cancelar entrega
  cancelarEntregaBtn.addEventListener("click", () => {
    const confirmarCancel = confirm("¿Seguro que deseas cancelar la entrega?");
    if (confirmarCancel) {
      actividadTexto.innerHTML = "<h1 class='anulado-texto'>HAS ANULADO TU ENTREGA</h1>";
      subirArchivoBtn.classList.remove("disabled");
      subirArchivoBtn.textContent = "Subir archivo";
      cancelarEntregaBtn.classList.add("d-none"); // Ocultar botón cancelar
      inputPDF.value = ""; // Limpiar archivo
      fileInfo.innerHTML = "";
    }
  });
});
