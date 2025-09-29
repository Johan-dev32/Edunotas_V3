// === PREVISUALIZAR IMAGEN O PDF ===
const fileInput = document.getElementById('fileInput');
const preview = document.getElementById('preview');
const uploadArea = document.getElementById('uploadArea');

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  preview.innerHTML = ""; // limpiar

  if (!file) return;

  uploadArea.querySelector("i").style.display = "none";
  uploadArea.querySelector("p").style.display = "none";
  uploadArea.querySelector("button").style.display = "none";

  if (file.type.includes("image")) {
    const reader = new FileReader();
    reader.onload = e => {
      const img = document.createElement("img");
      img.src = e.target.result;
      img.classList.add("img-fluid", "rounded");
      preview.appendChild(img);
    };
    reader.readAsDataURL(file);
  } else if (file.type === "application/pdf") {
    preview.innerHTML = `
      <div class="pdf-preview text-center">
        <i class="bi bi-file-earmark-pdf-fill text-danger fs-1"></i>
        <p>${file.name}</p>
      </div>`;
  } else {
    preview.innerHTML = `<p class="text-danger">Formato no válido</p>`;
  }
});


// === CONFIRMAR PUBLICACIÓN ===
const btnPublicar = document.getElementById("btnPublicar");
const confirmModal = document.getElementById("confirmModal");
const confirmText = document.getElementById("confirmText");
const cancelSend = document.getElementById("cancelSend");
const confirmSend = document.getElementById("confirmSend");

btnPublicar.addEventListener("click", () => {
const titulo = document.querySelector("input[placeholder='Escribe el título de la noticia']").value;
const contenido = document.querySelector("textarea[placeholder='Escribe aquí tu noticia...']").value;
const autor = document.querySelector("input[placeholder='Nombre del autor']").value || "Anónimo";

  // Mostrar el modal
  confirmText.textContent = `¿Quieres publicar la noticia "${titulo}" creada por ${autor}?`;
  confirmModal.style.display = "flex";
});

// Cancelar modal
cancelSend.addEventListener("click", () => {
  confirmModal.style.display = "none";
});

// Confirmar envío
confirmSend.addEventListener("click", () => {
  confirmModal.style.display = "none";
  alert("✅ ¡Noticia publicada con éxito!");
});
function renderNoticias() {
  const noticias = JSON.parse(localStorage.getItem("noticias")) || [];
  const container = document.querySelector(".row.g-3");

  // Elimina las tarjetas anteriores
  container.innerHTML = "";

  noticias.forEach((n, index) => {
    container.innerHTML += `
      <div class="col-md-6">
        <div class="card p-3 shadow-sm h-100">
          ${n.imagen ? `<img src="${n.imagen}" class="img-fluid rounded mb-2">` : ""}
          <h5>${n.titulo}</h5>
          <small class="text-muted">${n.fecha} | Por: ${n.creadoPor}</small>
          <p class="mt-2">${n.contenido}</p>
        </div>
      </div>
    `;
  });
}

// Ejecutar al cargar la página
renderNoticias();