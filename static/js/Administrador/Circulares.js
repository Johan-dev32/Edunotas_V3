// Circulares.js
document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("fileUpload");
  const btnSubir = document.getElementById("btnSubirDocumento");

  // Crear preview
  const uploadBox = document.querySelector(".upload-box");
  const previewContainer = document.createElement("div");
  previewContainer.classList.add("mt-3", "text-center");
  uploadBox.appendChild(previewContainer);

  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    previewContainer.innerHTML = "";

    if (file) {
      const fileName = document.createElement("p");
      fileName.textContent = `Archivo seleccionado: ${file.name}`;
      fileName.classList.add("fw-bold");
      previewContainer.appendChild(fileName);

      if (file.type.startsWith("image/")) {
        const imgPreview = document.createElement("img");
        imgPreview.src = URL.createObjectURL(file);
        imgPreview.classList.add("img-fluid", "rounded", "shadow-sm", "mt-2");
        imgPreview.style.maxHeight = "200px";
        previewContainer.appendChild(imgPreview);
      }

      if (file.type === "application/pdf") {
        const pdfPreview = document.createElement("embed");
        pdfPreview.src = URL.createObjectURL(file);
        pdfPreview.type = "application/pdf";
        pdfPreview.classList.add("mt-2", "border", "rounded");
        pdfPreview.style.width = "100%";
        pdfPreview.style.height = "300px";
        previewContainer.appendChild(pdfPreview);
      }
    }
  });

  // 🔹 Modal dinámico
  const confirmModal = document.createElement("div");
  confirmModal.className = "custom-modal";
  confirmModal.style.cssText = `
    display: none;
    position: fixed; 
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.6); 
    justify-content: center; 
    align-items: center;
    z-index: 1050;
  `;
  confirmModal.innerHTML = `
    <div class="bg-white rounded shadow p-4" style="max-width: 400px; width: 90%;">
      <div class="d-flex align-items-center mb-3">
        <i class="bi bi-exclamation-triangle-fill text-warning fs-4 me-2"></i>
        <h5 class="m-0 fw-bold">Confirmar envío</h5>
      </div>
      <p id="confirmText" class="mb-2"></p>
      <p class="mb-0">¿Deseas continuar?</p>
      <div class="d-flex justify-content-end gap-2 mt-3">
        <button id="cancelSend" class="btn btn-secondary">Cancelar</button>
        <button id="confirmSend" class="btn btn-danger">Subir</button>
      </div>
    </div>
  `;
  document.body.appendChild(confirmModal);

  const confirmText = confirmModal.querySelector("#confirmText");
  const cancelSend = confirmModal.querySelector("#cancelSend");
  const confirmSend = confirmModal.querySelector("#confirmSend");

  // 📌 Botón subir
  btnSubir.addEventListener("click", (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
      alert("⚠️ Por favor selecciona un documento antes de subir.");
      return;
    }

    confirmText.textContent = `Archivo: ${file.name}`;
    confirmModal.style.display = "flex";
  });

  // 📌 Botón cancelar
  cancelSend.addEventListener("click", () => {
    confirmModal.style.display = "none";
  });

  // 📌 Botón confirmar → guardar en localStorage y redirigir
  confirmSend.addEventListener("click", () => {
    confirmModal.style.display = "none";

    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = e => {
      const fileData = {
        name: file.name,
        type: file.type,
        data: e.target.result
      };

      // Guardamos la circular en localStorage
      localStorage.setItem("circular1", JSON.stringify(fileData));

      alert("✅ Documento subido correctamente");
      window.location.href = "/paginainicio";
    };

    reader.readAsDataURL(file);
  });
});
