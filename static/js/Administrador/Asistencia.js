document.addEventListener("DOMContentLoaded", () => {
  const contenido = document.getElementById("contenido-justificacion");
  const btnEditar = document.getElementById("btnEditar");
  const btnGuardar = document.getElementById("btnGuardar");
  const btnSubir = document.getElementById("btnSubir");
  const btnVerPDF = document.getElementById("btnVerPDF");
  const inputComprobante = document.getElementById("comprobante");

  const confirmModal = new bootstrap.Modal(document.getElementById("confirmModal"));
  const detalleJustificacion = document.getElementById("detalleJustificacion");
  const btnConfirmarSubida = document.getElementById("btnConfirmarSubida");

  // Editar texto
  btnEditar.addEventListener("click", () => {
    contenido.contentEditable = true;
    contenido.classList.add("editando");
    btnEditar.disabled = true;
    btnGuardar.disabled = false;
  });

  // Guardar texto
  btnGuardar.addEventListener("click", () => {
    contenido.contentEditable = false;
    contenido.classList.remove("editando");
    btnEditar.disabled = false;
    btnGuardar.disabled = true;
    alert("✅ Justificación actualizada correctamente");
  });

  // Abrir modal al dar click en Subir
  btnSubir.addEventListener("click", () => {
    const fecha = document.getElementById("fecha")?.value || "Sin fecha";
    const titulo = document.getElementById("titulo")?.value || "Sin título";
    const contenidoTexto = contenido.innerText.substring(0, 20) + "...";
    const archivo = inputComprobante.files[0]?.name || "Ningún archivo seleccionado";

    detalleJustificacion.innerText = 
      `📅 Fecha: ${fecha}\n📝 Título: ${titulo}\n📄 Contenido: ${contenidoTexto}\n📎 Documento: ${archivo}`;

    confirmModal.show();
  });

  // Confirmar envío desde el modal
  btnConfirmarSubida.addEventListener("click", () => {
    confirmModal.hide();
    alert("📤 Justificación enviada correctamente");
  });

  // Ver PDF
  btnVerPDF.addEventListener("click", () => {
    const archivo = inputComprobante.files[0];
    if (!archivo) {
      alert("⚠️ Primero selecciona un archivo de comprobante");
      return;
    }
    const url = URL.createObjectURL(archivo);
    window.open(url, "_blank");
  });
});
